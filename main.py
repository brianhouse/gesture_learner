#!/usr/bin/env python3

import sys, queue
import Leap
from random import random
from housepy import animation, osc, config, log


class Listener(Leap.Listener):

    def __init__(self):
        Leap.Listener.__init__(self)
        self.queue = queue.Queue()
        self.hand_position = None
        self.finger_positions = None

    def on_connect(self, controller):
        log.info("Connected")

    def on_frame(self, controller):
        frame = controller.frame()
        # print("Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (frame.id, frame.timestamp, len(frame.hands), len(frame.fingers)))
        if not len(frame.hands):
            return
        hand = frame.hands[0]
        self.hand_position = hand.palm_position.to_tuple()
        # self.hand_transform = Leap.Matrix(hand.basis.x_basis, hand.basis.y_basis, hand.basis.z_basis).rigid_inverse()
        self.finger_positions = []        
        for finger in hand.fingers:
            joint_positions = []             
            joint_positions.append(self.scale(self.transform(finger.tip_position).to_tuple()))
            joint_positions.append(self.scale(self.transform(finger.bone(finger.JOINT_TIP).prev_joint).to_tuple()))
            joint_positions.append(self.scale(self.transform(finger.bone(finger.JOINT_DIP).prev_joint).to_tuple()))
            joint_positions.append(self.scale(self.transform(finger.bone(finger.JOINT_PIP).prev_joint).to_tuple()))
            self.finger_positions.append(joint_positions)
        self.queue.put((self.hand_position, self.finger_positions))
        # data = self.flatten(self.finger_positions)
        # log.info("/joints %s" % len(data))
        # sender.send("/joints", data)

    def transform(self, joint):
        return joint
        # return self.hand_transform.transform_point(joint)

    def scale(self, joint):
        hx, hy, hz = self.hand_position
        hx = (hx + 250) / 500
        hy = (hy + 250) / 500
        hz = (hz + 250) / 500                

        x, y, z = joint
        x = (((x + 250) / 500) - hx) * 2 + 0.5
        y = (((y + 250) / 500) - hy) * 2 + 0.5
        z = (((z + 250) / 500) - hz) * 2 + 0.5

        # x, y, z = joint
        # x = (((x + 250) / 500)) * 2 + 0.5
        # y = (((y + 250) / 500)) * 2 + 0.5
        # z = (((z + 250) / 500)) * 2 + 0.5

        return x, y, z

    def flatten(self, fingers):
        out = []
        for finger in fingers:
            for joint in finger:
                for dimension in joint:                
                    out.append(dimension)
        return out



listener = Listener()
controller = Leap.Controller()
controller.add_listener(listener)

osc.verbose = False
sender = osc.Sender(config['port'])


hand_position = None
finger_positions = None
def draw():
    global hand_position
    global finger_positions
    # ctx.translate(-1., -0.85, -1.5)        
    ctx.translate(-0.5, -0.5, -1.5)
    ctx.rotate(*rotation_x)
    ctx.rotate(*rotation_y)    
    while True:
        try:
            hand_position, finger_positions = listener.queue.get_nowait()
        except queue.Empty:
            break
    # ctx.rect(scale(x), scale(y), 10/ctx.width, 10/ctx.height, color=(1., 0., 0., 1.))
    if finger_positions is not None:
        for finger in finger_positions:
            # print(finger)
            for j, joint in enumerate(finger):
                x, y, z = joint
                # print(x, y, z)
                # ctx.rect(x - (3/ctx.width), y - (3/ctx.height), 5/ctx.width, 5/ctx.height)
                if j == 0:
                    continue
                x2, y2, z2 = finger[j-1]
                # ctx.line(x, y, x2, y2, thickness=7)    
                ctx.line3D(x, y, z, x2, y2, z2, thickness=20, color=(1., 1., 1., 1.))   
    ctx.line3D(0, 0, 0, 1, 0, 0, thickness=1, color=(1., 0., 0., 1.))
    ctx.line3D(0, 0, 0, 0, 1, 0, thickness=1, color=(0., 1., 0., 1.))
    ctx.line3D(0, 0, 0, 0, 0, 1, thickness=1, color=(0., 0., 1., 1.))

rotation_x = 0, 0, 0, 0
rotation_y = 0, 0, 0, 0
rotation_z = 0, 0, 0, 0
# rotation_x, rotation_y = (-53.0, 0, 1, 0), (13.5, 1, 0, 0)
ctx = animation.Context(600, 600, background=(0., 0., 0., 1.), _3d=True)
def on_mouse_drag(data):
    x, y, dx, dy, button, modifers = data
    global rotation_x, rotation_y
    SCALE = -0.5
    rotation_x = (dx * SCALE) + rotation_x[0], 0, 1, 0
    rotation_y = (dy * SCALE) + rotation_y[0], 1, 0, 0
    print(rotation_x, rotation_y)
ctx.add_callback("mouse_drag", on_mouse_drag)    
ctx.start(draw)







"""

next:
- do the scaling in the frame, not the animation, so you can send the normalized positions as OSC.
- visualize 3D

"""
