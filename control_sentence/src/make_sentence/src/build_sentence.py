#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Point
from make_sentence.msg import sentence
from make_sentence.msg import Obj
from collections import deque
import random

class MultimodalSentenceBuilder:
    def __init__(self):
       # Flags and storage for coordinate data
        self.coordinates_enabled_1 = False
        self.coordinates_enabled_2 = False
        self.coordinate_data_1 = None
        self.coordinate_data_1_index = None
        self.string_data_1 = None
        self.coordinate_data_2 = None
        self.coordinate_data_2_index = None
        self.string_data_2 = None
        self.string_data_3 = None # speed (e.g., high or low)
        self.string_data_4 = None  # angle
        self.finish_flag = False
        self.words = deque() # stores intermediate recognized words
        self.target_object = Point()

        # Subscribers and Publisher
        self.coordinate_subscriber = rospy.Subscriber('/closest_point', Obj, self.coordinate_callback)
        self.string_subscriber = rospy.Subscriber('speech_recognition/final_result', String, self.string_callback)
        self.custom_publisher = rospy.Publisher('control_sentence', sentence, queue_size=100)
    
    def coordinate_callback(self, data):
        # Handles coordinate data when specific flags are enabled
        if self.coordinates_enabled_1 and not self.coordinates_enabled_2:
            self.coordinate_data_1 = Point()
            self.coordinate_data_2_index = int()
            print("Get 1. Subcommand")
            self.coordinate_data_1.x = data.point.x
            self.coordinate_data_1.y = data.point.y
            self.coordinate_data_1.z = data.point.z
            self.coordinate_data_1_index = data.obj_index
            self.coordinates_enabled_1 = False
            
        elif self.coordinates_enabled_2 and not self.coordinates_enabled_1:
            self.coordinate_data_2 = Point()
            self.coordinate_data_2_index = int()
            print("Get 2. Subcommand")
            self.coordinate_data_2.x = data.point.x
            self.coordinate_data_2.y = data.point.y
            self.coordinate_data_2.z = data.point.z
            self.coordinate_data_2_index = data.obj_index
            self.coordinates_enabled_2 = False
    def string_callback(self, data):
        # Handles recognized speech and updates internal state based on key words
        word = data.data
        if word == 'this' or word == 'here':
            self.string_data_1 = self.words[0] # first object/action keyword
            self.coordinates_enabled_1 = True
            self.coordinates_enabled_2 = False
        elif word == 'there':
            self.string_data_2 = self.words[1] # second object/action keyword
            self.coordinates_enabled_1 = False
            self.coordinates_enabled_2 = True
            #self.words.clear()
        elif word == 'home' or word == 'throw':
            self.string_data_1 = word # single-word command
            self.string_data_2 = None
            self.coordinates_enabled_1 = False
            self.coordinates_enabled_2 = False
            #self.words.clear()
        elif word == 'high' or word == 'low':
        
            self.string_data_3 = word # speed
            self.coordinates_enabled_1 = False
            self.coordinates_enabled_2 = False
        elif word =='finish':
            if 'angle' in self.words:
                index = self.words.index("angle")
                self.string_data_4 = self.words[index+1]    
            self.finish_flag = True
            
            # self.words.clear()
        else:
            # Buffer word for later use
            self.words.append(word)

    def run(self):
        # Main loop that waits for finish command to publish the sentence
        try:
            
            control_sentence = sentence()
            
            print("wait for control sentence")
            while not rospy.is_shutdown():
                if self.finish_flag is True:
                    control_sentence.action1 = "none"
                    control_sentence.obj_index_1 = -1
                    control_sentence.position1.x = 0
                    control_sentence.position1.y = 0
                    control_sentence.position1.z = 0
                    control_sentence.position2.x = 0
                    control_sentence.position2.y = 0
                    control_sentence.position2.z = 0
                    control_sentence.action2 = "none"
                    control_sentence.obj_index_2 = -1
                    control_sentence.speed = "none"
                    control_sentence.angle = "none"
                    # Populate sentence based on gathered data
                    if self.string_data_1:
                        control_sentence.action1 = self.string_data_1
                    if self.coordinate_data_1:
                        control_sentence.position1 = self.coordinate_data_1
                        control_sentence.obj_index_1 = self.coordinate_data_1_index
                    if self.string_data_2:
                        control_sentence.action2 = self.string_data_2
                    if self.coordinate_data_2:
                        control_sentence.position2 = self.coordinate_data_2
                        control_sentence.obj_index_2 = self.coordinate_data_2_index
                    if self.string_data_3:
                        control_sentence.speed = self.string_data_3
                    if self.string_data_4:
                        control_sentence.angle = self.string_data_4
                    # Publish constructed control sentence
                    self.custom_publisher.publish(control_sentence)

                    # Log info for debugging
                    rospy.loginfo("control sentence:" + str(control_sentence.action1))
                    rospy.loginfo("control sentence:" + str(control_sentence.position1))
                    rospy.loginfo("control sentence:" + str(control_sentence.action2))
                    rospy.loginfo("control sentence:" + str(control_sentence.position2))
                    rospy.loginfo("control sentence:" + str(control_sentence.speed))
                    rospy.loginfo("control sentence:" + str(control_sentence.angle))
                    
                    # Reset internal state
                    self.coordinate_data_1 = None
                    self.string_data_1 = None
                    self.coordinate_data_2 = None
                    self.string_data_2 = None
                    self.string_data_3 = None
                    self.string_data_4 = None
                    self.words.clear()
                    self.finish_flag = False
                    
        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))
        except KeyboardInterrupt:
            rospy.loginfo("Stopping the make_sentence node...")
            rospy.sleep(1)
            print("node terminated")


def main():
    rospy.init_node('MultimodalSentence_Builder')
    Builder = MultimodalSentenceBuilder()
    Builder.run()
    rospy.spin()

if __name__ == '__main__':
    main()
