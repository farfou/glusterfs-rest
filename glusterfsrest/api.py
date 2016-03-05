# -*- coding: utf-8 -*-
"""
    api.py

    :copyright: (c) 2014 by Aravinda VK
    :license: MIT, see LICENSE for more details.
"""

from flask import render_template
from glusterfsrest.restapp import app, requires_auth, get_post_data
from glusterfsrest.restapp import run_and_response
from glusterfsrest.cli import volume, peer
from glusterfsrest.fs.xfs import Xfs
import yaml
import os
import lvm


@app.route("/api/<float:version>/lvm/<string:vg_name>/thinpool/<string:pool_name>", methods=['POST'])
def createLvThinVolume(version, vg_name, pool_name, size):
    vg = lvm.vgOpen(vg_name, 'w')
    vg.createLvThinpool(pool_name, size)
    vg.close()
    return

@app.route("/api/<float:version>/lvm/<string:vg_name>/lv/<string:lv_name>", methods=['POST'])
def createThinVolume(version, vg_name, lv_name):
    vg = lvm.vgOpen(vg_name,'w')
    thinpoolname = get_post_data('thinpool', '')
    size = int(get_post_data('size', 1000000))
    vg.createLvThin(thinpoolname, lv_name, size)
    vg.close()
    return


@app.route("/api/<float:version>/lvm/<string:vg_name>/lv/<string:lv_name>/format", methods=['POST'])
def formatThinVolumeAndMount(version, vg_name, lv_name):
    devPath = '/dev/' + vg_name + '/' + lv_name;
    mountPoint = get_post_data('mount_point', '/mnt/vol/' + lv_name)
    fs_conf = dict()
    fs_conf["dev_file"] = devPath
    fs_conf["type"] = 'xfs'
    fs_conf["mount_point"] = mountPoint
    fs_conf["mount_option"] = ""
    # -i size=512


    ### Create mount point !
    ###
    ###


    xfsVol = Xfs(vg_name + '/' + lv_name, fs_conf)
    xfsVol.mkfs('xfs', devPath, '-i size=512')
    os.makedirs(mountPoint)
    xfsVol.mount()
    #create subdir
    xfsVol.create_dir('/content')
    return


@app.route("/api/<float:version>/doc")
def showdoc(version):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "doc/api-%s.yml" % version)
    apis = yaml.load(open(filename))
    return render_template("doc-%s.html" % version, apis=apis['apis'])


@app.route("/api/<float:version>/volume/<string:name>", methods=["POST"])
@requires_auth(['glusterroot', 'glusteradmin'])
def volume_create(version, name):
    bricks_str = get_post_data('bricks', '')
    bricks = [b.strip() for b in bricks_str.split(",")]
    replica = get_post_data('replica', 0)
    stripe = get_post_data('stripe', 0)
    transport = get_post_data('transport', 'tcp').lower()
    force = get_post_data('force', False)
    start = get_post_data('start', False)

    return run_and_response(volume.create, [name, bricks, replica,
                                            stripe, transport, force, start])


@app.route("/api/<float:version>/volume/<string:name>", methods=["DELETE"])
@requires_auth(['glusterroot'])
def volume_delete(version, name):
    stop = get_post_data('stop', False)
    return run_and_response(volume.delete, [name, stop])


@app.route("/api/<float:version>/volume/<string:name>/start",
           methods=["PUT"])
@requires_auth(['glusterroot', 'glusteradmin'])
def volume_start(version, name):
    force = get_post_data('force', False)
    return run_and_response(volume.start, [name, force])


@app.route("/api/<float:version>/volume/<string:name>/stop",
           methods=["PUT"])
@requires_auth(['glusterroot', 'glusteradmin'])
def volume_stop(version, name):
    force = get_post_data('force', False)
    return run_and_response(volume.stop, [name, force])


@app.route("/api/<float:version>/volume/<string:name>/restart",
           methods=["PUT"])
@requires_auth(['glusterroot', 'glusteradmin'])
def volume_restart(version, name):
    return run_and_response(volume.restart, [name])


@app.route("/api/<float:version>/volumes", methods=["GET"])
@requires_auth(['glusterroot', 'glusteradmin', 'glusteruser'])
def volumes_get(version):
    return run_and_response(volume.info, [])


@app.route("/api/<float:version>/volume/<string:name>", methods=["GET"])
@requires_auth(['glusterroot', 'glusteradmin', 'glusteruser'])
def volume_get(version, name):
    return run_and_response(volume.info, [name])


@app.route("/api/<float:version>/peers", methods=["GET"])
@requires_auth(['glusterroot', 'glusteradmin', 'glusteruser'])
def peers_get(version):
    return run_and_response(peer.info, [])


@app.route("/api/<float:version>/peer/<string:hostname>", methods=["POST"])
@requires_auth(['glusterroot', 'glusteradmin'])
def peer_create(version, hostname):
    return run_and_response(peer.attach, [hostname])


@app.route("/api/<float:version>/peer/<string:hostname>", methods=["DELETE"])
@requires_auth(['glusterroot'])
def peer_delete(version, hostname):
    force = get_post_data('force', False)
    return run_and_response(peer.detach, [hostname, force])
