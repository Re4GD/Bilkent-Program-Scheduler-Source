"""
    Bilkent Program Scheduler version 1.5.1 Pandemic Edition
    Copyright (C) 2020  Can Gürsu

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfile, asksaveasfile
import tkinter.font as font
import json
import numpy as np
import itertools
import random
import pyscreeze
import requests
import threading
import time

try:
    with open("lectures.json", "r") as f:
        lecture_dict = json.load(f)
        print("Data File Found!\n")
except FileNotFoundError:
    print("No Data File!\nPlease Select A Semester File!\n")
    lecture_dict = {}

VERSION = 2

"""
General Information About Courses/Lectures

# Course Code      : ME
# Lecture ID       : ME 232
# Lecture Code     : 232
# Lecture Section  : 1
# Lecture Full Name: ME 232-1

Versions
Version 1 - 1.5.0: Release
Version 2 - 1.5.1: Pandemic Edition Patch 
"""


# Display Combinations
def display_combs():
    """
    Display function
    :return: None
    """
    print("All   Combinations:", len(all_combinations))
    # print(all_combinations)
    print("Valid Combinations:", len(valid_combinations))
    # print(valid_combinations)
    print()


# Create Lecture ID Buttons
def add_lecture_id_buttons(course_name):
    """
    Add Course Code buttons to Lecture ID Frame
    :param course_name:
    :return: None
    """
    delete_lecture_id_buttons()

    lecture_id_list = []

    try:
        for key in lecture_dict[course_name].keys():
            pos = key.find("-")
            key = key[:pos]
            if key not in lecture_id_list:
                lecture_id_list.append(key)

        # Course Buttons
        def_relx_counter = 0.05  # Starting x pos
        def_rely_counter = 0.05  # Starting y pos
        def_max_course_col = 6  # Max column number
        def_course_col = 0  # Column counter

        for lec_id in lecture_id_list:
            lec = tk.Button(frame_lecture_id, text=lec_id, padx=20, pady=10,
                            command=lambda l_id=lec_id: add_lecture_to_scheduler(l_id))
            lec.place(relwidth=0.15, relheight=0.075, relx=def_relx_counter, rely=def_rely_counter)

            def_course_col += 1
            def_relx_counter += 0.15

            if def_course_col == def_max_course_col:
                def_rely_counter += 0.075
                def_relx_counter = 0.05
                def_course_col = 0

    except AttributeError:
        tk.Label(frame_lecture_id, text="NO LECTURE", fg="red", bg=frame_background_color, font=bold)\
            .place(relwidth=0.2, relheight=0.2, relx=0.4, rely=0.1)


# Delete Lecture ID Buttons
def delete_lecture_id_buttons():
    for child in frame_lecture_id.winfo_children():
        if child.winfo_class() == 'Button' or child.winfo_class() == 'Label':
            child.destroy()


# Add Lecture Info and Update Scheduler
def add_lecture_to_scheduler(course_name):
    """
    Add new course, call new_course(), add button for new course's information to Lecture Info Frame,
    and call update_scheduler() to update the Scheduler Frame
    :param course_name:
    :return: None
    """

    global current_comb_num
    global current_comb
    global old_comb

    current_comb_num = 1

    lecture_info = tk.StringVar()

    # REFRESH
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button" and course_name in child.cget("text"):
            break
    else:
        new_course(course_name)

        delete_lecture_info_buttons()

        if valid_combinations:
            old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
            for l in list(valid_combinations[current_comb_num - 1]):
                # print(l)
                c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

                course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                # Display
                if str(c_name) in str(course_name):
                    print("ADDED\n{}-{}\n".format(c_name, c_section))

                    display_combs()

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                     c_section, course_teacher)
                # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                          fill=tk.X)

        else:
            nav_info.set("0/0")
            old_comb, current_comb, current_comb_num = [], [], -1

    update_scheduler()
    extend_undo_redo()


# Delete Button when clicked
def delete_lecture_from_scheduler(course_name):
    """
    Delete the course, call del_course(), delete course's information button from Lecture Info Frame,
    and update the Scheduler Frame
    :param course_name:
    :return: None
    """

    global current_comb_num
    global current_comb
    global old_comb

    current_comb_num = 1

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button" and course_name in str(child.cget("text")):
            # Display
            display = str(child.cget("text")).split(" ")[0] + " " + str(child.cget("text")).split(" ")[1]
            print("DELETED\n{}\n".format(display))
            child.destroy()
            break

    del_course()

    # Display
    display_combs()

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            break
    else:
        nav_info.set("0/0")
        old_comb, current_comb, current_comb_num = [], [], -1

    delete_lecture_info_buttons()

    if valid_combinations:
        old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
        if valid_combinations[current_comb_num - 1]:
            for l in list(valid_combinations[current_comb_num - 1]):
                # print(l)
                c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

                course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                     c_section, course_teacher)
                # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                          fill=tk.X)

    update_scheduler()
    extend_undo_redo()


# Add New Course
def new_course(course_name):
    """
    Look in the Lecture Information Frame, add the new course, fetch all lecture data,
    create a list with the lecture data (lec_list), and call available_course(lec_list)
    :return: None
    """
    lecture_list = []

    new_lecture_id = str(course_name)
    new_course_code, new_lecture_code = str(new_lecture_id).split(" ")
    lecture_list.append([l for l in lecture_dict[new_course_code].keys() if str(course_name) in l])

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))  # ME 232
            def_course_code = str(button_text).split(" ")[0]  # ME
            def_lecture_code = str(button_text).split(" ")[1][:3]  # 232
            if new_course_code + " " + new_lecture_code != def_course_code + " " + def_lecture_code:
                lecture_list.append([l for l in lecture_dict[def_course_code].keys()
                                     if def_course_code + " " + def_lecture_code in l])

    available_course(lecture_list)


# Delete New Course
def del_course():
    """
    Look in the Lecture Information Frame, delete the course, fetch all lecture data,
    create a list with the lecture data (lec_list), and call available_course(lec_list)
    :return: None
    """
    available_course(current_lectures())


# Find Available Courses
def available_course(l_list):
    """
    Get the lecture list, and check the Scheduler Frame. Create valid programs,
    and make the valid_combinations list a global
    :param l_list:
    :return: None
    """
    global valid_combinations, all_combinations

    global current_comb_num
    global current_comb
    global old_comb

    all_combinations = []
    valid_combinations = []

    if l_list:
        all_combinations = list(itertools.product(*l_list))

        for c in all_combinations:
            combination_failed = False
            binary_list = np.zeros((13, 7))
            for l in c:
                course_binary = np.zeros((13, 7))
                def_course_code = l.split(" ")[0]
                for t in lecture_dict[def_course_code][l][1:len(lecture_dict[def_course_code])]:
                    if t != "INVALID":
                        day = t.split(" ")[0]
                        specific_t = t.split(" ")[1]
                        start, finish = specific_t.split("-")

                        start_hour = int(start.split(":")[0])
                        finish_hour = int(finish.split(":")[0])

                        for h in range(start_hour, finish_hour):
                            if h == 12:
                                continue

                            # Monday
                            if "Mon" == day:
                                if h == 8:
                                    course_binary[0][0] = 1 if monday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][0] = 1 if monday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][0] = 1 if monday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][0] = 1 if monday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][0] = 1 if monday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][0] = 1 if monday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][0] = 1 if monday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][0] = 1 if monday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][0] = 1 if monday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][0] = 1 if monday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][0] = 1 if monday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][0] = 1 if monday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][0] = 1 if monday_buttons[13].cget("text") != "X" else 2
                            # Tuesday
                            elif "Tue" == day:
                                if h == 8:
                                    course_binary[0][1] = 1 if tuesday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][1] = 1 if tuesday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][1] = 1 if tuesday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][1] = 1 if tuesday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][1] = 1 if tuesday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][1] = 1 if tuesday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][1] = 1 if tuesday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][1] = 1 if tuesday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][1] = 1 if tuesday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][1] = 1 if tuesday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][1] = 1 if tuesday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][1] = 1 if tuesday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][1] = 1 if tuesday_buttons[13].cget("text") != "X" else 2
                            # Wednesday
                            elif "Wed" == day:
                                if h == 8:
                                    course_binary[0][2] = 1 if wednesday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][2] = 1 if wednesday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][2] = 1 if wednesday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][2] = 1 if wednesday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][2] = 1 if wednesday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][2] = 1 if wednesday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][2] = 1 if wednesday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][2] = 1 if wednesday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][2] = 1 if wednesday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][2] = 1 if wednesday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][2] = 1 if wednesday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][2] = 1 if wednesday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][2] = 1 if wednesday_buttons[13].cget("text") != "X" else 2
                            # Thursday
                            elif "Thu" == day:
                                if h == 8:
                                    course_binary[0][3] = 1 if thursday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][3] = 1 if thursday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][3] = 1 if thursday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][3] = 1 if thursday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][3] = 1 if thursday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][3] = 1 if thursday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][3] = 1 if thursday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][3] = 1 if thursday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][3] = 1 if thursday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][3] = 1 if thursday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][3] = 1 if thursday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][3] = 1 if thursday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][3] = 1 if thursday_buttons[13].cget("text") != "X" else 2
                            # Friday
                            elif "Fri" == day:
                                if h == 8:
                                    course_binary[0][4] = 1 if friday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][4] = 1 if friday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][4] = 1 if friday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][4] = 1 if friday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][4] = 1 if friday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][4] = 1 if friday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][4] = 1 if friday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][4] = 1 if friday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][4] = 1 if friday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][4] = 1 if friday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][4] = 1 if friday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][4] = 1 if friday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][4] = 1 if friday_buttons[13].cget("text") != "X" else 2
                            # Saturday
                            elif "Sat" == day:
                                if h == 8:
                                    course_binary[0][5] = 1 if saturday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][5] = 1 if saturday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][5] = 1 if saturday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][5] = 1 if saturday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][5] = 1 if saturday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][5] = 1 if saturday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][5] = 1 if saturday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][5] = 1 if saturday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][5] = 1 if saturday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][5] = 1 if saturday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][5] = 1 if saturday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][5] = 1 if saturday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][5] = 1 if saturday_buttons[13].cget("text") != "X" else 2
                            # Sunday
                            elif "Sun" == day:
                                if h == 8:
                                    course_binary[0][6] = 1 if sunday_buttons[0].cget("text") != "X" else 2
                                elif h == 9:
                                    course_binary[1][6] = 1 if sunday_buttons[1].cget("text") != "X" else 2
                                elif h == 10:
                                    course_binary[2][6] = 1 if sunday_buttons[2].cget("text") != "X" else 2
                                elif h == 11:
                                    course_binary[3][6] = 1 if sunday_buttons[3].cget("text") != "X" else 2
                                elif h == 13:
                                    course_binary[4][6] = 1 if sunday_buttons[5].cget("text") != "X" else 2
                                elif h == 14:
                                    course_binary[5][6] = 1 if sunday_buttons[6].cget("text") != "X" else 2
                                elif h == 15:
                                    course_binary[6][6] = 1 if sunday_buttons[7].cget("text") != "X" else 2
                                elif h == 16:
                                    course_binary[7][6] = 1 if sunday_buttons[8].cget("text") != "X" else 2
                                elif h == 17:
                                    course_binary[8][6] = 1 if sunday_buttons[9].cget("text") != "X" else 2
                                elif h == 18:
                                    course_binary[9][6] = 1 if sunday_buttons[10].cget("text") != "X" else 2
                                elif h == 19:
                                    course_binary[10][6] = 1 if sunday_buttons[11].cget("text") != "X" else 2
                                elif h == 20:
                                    course_binary[11][6] = 1 if sunday_buttons[12].cget("text") != "X" else 2
                                elif h == 21:
                                    course_binary[12][6] = 1 if sunday_buttons[13].cget("text") != "X" else 2

                            if 2 in binary_list:
                                combination_failed = True
                                break
                            else:
                                # Teacher Blacklist
                                if teacher_blacklist:
                                    for k in teacher_blacklist:
                                        if lecture_dict[def_course_code][l][0] in k:
                                            combination_failed = True
                                            break

                                # Section Blacklist
                                if l in section_blacklist:
                                    combination_failed = True
                                    break

                if combination_failed:
                    break
                else:
                    binary_list += course_binary
                    if 2 in binary_list:
                        break

            if 2 not in binary_list and not combination_failed:
                valid_combinations.append(c)

    if valid_combinations:
        nav_info.set("1/" + str(len(valid_combinations)))

        old_comb, current_comb = current_comb, valid_combinations[0]
        current_comb_num = 1
    else:
        nav_info.set("0/0")
        old_comb, current_comb, current_comb_num = [], [], -1


# Forward Button
def forward(number):
    """
    Iterate over the next valid combination.
    If number == 'last combination', set navigator to '1/last combination'.
    Create new forward/back buttons with appropriate numbers
    :param number:
    :return: None
    """

    global navigator
    global nav_info

    global button_back
    global button_forward

    global current_comb_num
    global current_comb
    global old_comb

    global valid_combinations

    # print(lecture_list)
    # available_course(lecture_list)

    if str(navigator.cget("text")) != "0/0":
        current_num = str(navigator.cget("text")).split("/")[0]
        next_num = int(current_num) + 1
        # print(current)
        # print(next_num)
        # print(len(valid_combinations))

        if int(current_num) == int(len(valid_combinations)):
            nav_info.set("1/" + str(len(valid_combinations)))
            current_comb_num = 1
            old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
        else:
            nav_info.set(str(next_num) + "/" + str(len(valid_combinations)))
            current_comb_num = next_num
            old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]

        for child in frame_lecture_info.winfo_children():
            if child.winfo_class() == "Button":
                child.destroy()

        # Display
        print("NAVIGATE FORWARD\nNavigating to Combination {}\n".format(current_comb_num))
        display_combs()

        old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
        if valid_combinations:
            for l in list(valid_combinations[current_comb_num - 1]):
                # print(l)
                c_code, c_section = str(l).split("-")
                c_name = str(c_code).split(" ")[0]
                c_key = str(c_code) + "-" + str(c_section)

                course_teacher = lecture_dict[c_name][c_key][0]
                # print(c_code, c_section, course_teacher)
                # c_hours = lecture_dict[c_name][c_key][1:len(lecture_dict[c_name][c_key])]
                # print(c_hours)

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1],
                                                     c_section, course_teacher)
                # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                          fill=tk.X)
        else:
            nav_info.set("0/0")
            old_comb, current_comb, current_comb_num = [], [], -1

        button_back.configure(text="<<", command=lambda: back(number - 1))
        button_forward.configure(text=">>", command=lambda: forward(number + 1))

        update_scheduler()


# Back Button
def back(number):
    """
    Iterate over the previous valid combination.
    If number == 'first combination', set navigator to 'last combination/last combination'.
    Create new forward/back buttons with appropriate numbers
    :param number:
    :return: None
    """
    global navigator
    global nav_info

    global button_back
    global button_forward

    global current_comb_num
    global current_comb
    global old_comb

    # print(lecture_list)
    # available_course(lecture_list)

    if str(navigator.cget("text")) != "0/0":
        current_num = str(navigator.cget("text")).split("/")[0]
        next_num = int(current_num) - 1
        # print(current)
        # print(len(valid_combinations)

        if int(current_num) == 1:
            nav_info.set(str(len(valid_combinations)) + "/" + str(len(valid_combinations)))
            current_comb_num = int(len(valid_combinations))
            old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
        else:
            nav_info.set(str(next_num) + "/" + str(len(valid_combinations)))
            current_comb_num = next_num
            old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]

        for child in frame_lecture_info.winfo_children():
            if child.winfo_class() == "Button":
                child.destroy()

        # Display
        print("NAVIGATE BACK\nNavigating to Combination {}\n".format(current_comb_num))
        display_combs()

        old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
        if valid_combinations:
            for l in list(valid_combinations[current_comb_num - 1]):
                # print(l)
                c_code, c_section = str(l).split("-")
                c_name = str(c_code).split(" ")[0]
                c_key = str(c_code) + "-" + str(c_section)

                course_teacher = lecture_dict[c_name][c_key][0]
                # print(c_code, c_section, course_teacher)
                # c_hours = lecture_dict[c_name][c_key][1:len(lecture_dict[c_name][c_key])]
                # print(c_hours)

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1],
                                                     c_section, course_teacher)
                # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                          fill=tk.X)
        else:
            nav_info.set("0/0")
            old_comb, current_comb, current_comb_num = [], [], -1

        # Navigator Buttons
        button_back.configure(text="<<", command=lambda: back(number - 1))
        button_forward.configure(text=">>", command=lambda: forward(number + 1))

        update_scheduler()


# Save Program
def save_program():
    """
    Save 'all_combinations', 'valid_combinations', 'button_status' to a pickle file
    :return: None
    """
    global valid_combinations
    global all_combinations
    global current_comb_num

    get_button_status()

    try:
        filename = asksaveasfile(filetypes=(("JSON Files", "*.json"), ("All files", "*.*")), defaultextension=".json")
        if "program" not in filename.name:
            raise AttributeError
        with open(filename.name, 'w') as prog:
            data_dict = dict()
            data_dict["all_combinations"] = all_combinations
            data_dict["valid_combinations"] = valid_combinations
            data_dict["teacher_blacklist"] = teacher_blacklist
            data_dict["section_blacklist"] = section_blacklist
            data_dict["btn_status_list"] = btn_status_list
            data_dict["version"] = VERSION
            json.dump(data_dict, prog)

        print("Successful Save!")
        print("\n---------------------------------------------------------------------\n")
        # print(all_combinations, valid_combinations, current_comb_num)

    except AttributeError:
        print("Couldn't Save! File name should contain 'program' in it!")
        print("\n---------------------------------------------------------------------\n")


# Load Program
def load_program():
    """
    Load 'all_combinations', 'valid_combinations', 'current_comb_num', 'button_status' from a pickle file
    :return: None
    """
    global all_combinations
    global valid_combinations
    global current_comb_num
    global teacher_blacklist
    global section_blacklist

    global btn_status_list

    try:
        filename = askopenfile()
        program = str(filename.name).rsplit("/", 1)[1]
        if "program" in str(program):
            with open(filename.name, "r") as prog:
                data_dict = json.loads(prog.read())

                try:
                    btn_status_list = data_dict.get("version")
                    all_combinations = data_dict.get("all_combinations")
                    valid_combinations = data_dict.get("valid_combinations")
                    teacher_blacklist = data_dict.get("teacher_blacklist")
                    section_blacklist = data_dict.get("section_blacklist")
                    btn_status_list = data_dict.get("btn_status_list")
                except KeyError:
                    # Version 1 program saves
                    messagebox.showerror("Version Error", "The program that you are trying to load is outdated. "
                                                          "Your lectures will not appear correctly. Sorry for the "
                                                          "inconvenience")
                    return

                if valid_combinations:
                    current_comb_num = 1
        else:
            raise IndexError

        if len(lecture_dict) == 0:
            raise ZeroDivisionError

        print("Successful Load!")
        print("\n---------------------------------------------------------------------\n")

        reset_scheduler_buttons()

        for l in valid_combinations[current_comb_num - 1]:
            c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]
            course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

            # Frame Lecture Info
            lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                 c_section, course_teacher)

            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                      fill=tk.X)

        set_button_status(btn_status_list)

        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))

        available_course(current_lectures())
        update_scheduler()

        reset_undo_redo()

    except IndexError:
        print("Couldn't Load! File name should contain 'program' in it!")
        print("\n---------------------------------------------------------------------\n")
    except ZeroDivisionError:
        print("Couldn't Load! Please import a semester file first!")
        print("\n---------------------------------------------------------------------\n")


# Undo
def undo():
    """
    Based on 'undo_redo_counter', go back to the previous program
    :return: None
    """
    global undo_redo_list, undo_redo_counter
    global old_comb, current_comb, current_comb_num
    global all_combinations, valid_combinations, teacher_blacklist, section_blacklist, btn_status_list

    btn_redo["state"] = tk.NORMAL
    undo_redo_display.set("")
    undo_redo_counter -= 1

    all_combinations = undo_redo_list[undo_redo_counter][0]
    valid_combinations = undo_redo_list[undo_redo_counter][1]
    teacher_blacklist = undo_redo_list[undo_redo_counter][2]
    section_blacklist = undo_redo_list[undo_redo_counter][3]
    btn_status_list = undo_redo_list[undo_redo_counter][4]

    reset_scheduler_buttons()
    delete_lecture_info_buttons()

    set_button_status(btn_status_list)

    if valid_combinations:
        nav_info.set("1/" + str(len(valid_combinations)))

        old_comb, current_comb = current_comb, valid_combinations[0]
        current_comb_num = 1
        for l in list(valid_combinations[0]):
            # print(l)
            c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

            course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

            # Frame Lecture Info
            lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                 c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                      fill=tk.X)
    else:
        nav_info.set("0/0")
        old_comb, current_comb, current_comb_num = [], [], -1

    print("UNDO\n")
    display_combs()

    update_scheduler()

    if undo_redo_counter == 0:
        btn_undo["state"] = tk.DISABLED
        undo_redo_display.set("NO UNDO'S LEFT")


# Redo
def redo():
    """
    Based on 'undo_redo_counter', go forward to the next program
    :return: None
    """
    global undo_redo_list, undo_redo_counter
    global old_comb, current_comb, current_comb_num
    global all_combinations, valid_combinations, teacher_blacklist, section_blacklist, btn_status_list

    btn_undo["state"] = tk.NORMAL
    undo_redo_display.set("")
    undo_redo_counter += 1

    all_combinations = undo_redo_list[undo_redo_counter][0]
    valid_combinations = undo_redo_list[undo_redo_counter][1]
    teacher_blacklist = undo_redo_list[undo_redo_counter][2]
    section_blacklist = undo_redo_list[undo_redo_counter][3]
    btn_status_list = undo_redo_list[undo_redo_counter][4]

    reset_scheduler_buttons()
    delete_lecture_info_buttons()

    set_button_status(btn_status_list)

    if valid_combinations:
        nav_info.set("1/" + str(len(valid_combinations)))

        old_comb, current_comb = current_comb, valid_combinations[0]
        current_comb_num = 1
        for l in list(valid_combinations[0]):
            # print(l)
            c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

            course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

            # Frame Lecture Info
            lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                 c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                      fill=tk.X)
    else:
        nav_info.set("0/0")
        old_comb, current_comb, current_comb_num = [], [], -1

    print("REDO\n")
    display_combs()

    update_scheduler()

    if undo_redo_counter == len(undo_redo_list) - 1:
        btn_redo["state"] = tk.DISABLED
        undo_redo_display.set("NO REDO'S LEFT")


def extend_undo_redo():
    global undo_redo_list, undo_redo_counter

    # if undo_redo_list[undo_redo_counter] != [all_combinations[:], valid_combinations[:], teacher_blacklist[:],
    #                                          section_blacklist[:], btn_status_list[:]]:
    btn_undo["state"] = tk.NORMAL
    btn_redo["state"] = tk.DISABLED
    undo_redo_display.set("")

    if undo_redo_counter != len(undo_redo_list) - 1:
        undo_redo_list = undo_redo_list[0:undo_redo_counter + 1]

    undo_redo_counter += 1
    get_button_status()
    undo_redo_list.append([all_combinations[:], valid_combinations[:], teacher_blacklist[:], section_blacklist[:],
                           btn_status_list[:]])


def reset_undo_redo():
    global undo_redo_list, undo_redo_counter
    get_button_status()
    undo_redo_list = [[all_combinations[:], valid_combinations[:], teacher_blacklist[:],
                       section_blacklist[:], btn_status_list[:]]]
    undo_redo_counter = 0
    undo_redo_display.set("")

    btn_redo["state"] = tk.DISABLED
    btn_undo["state"] = tk.DISABLED


def set_button_status(status_list):
    for b, s in zip(monday_buttons, status_list[0:14]):
        if s == "X":
            b.configure(text=s)
    for b, s in zip(tuesday_buttons, status_list[14:28]):
        if s == "X":
            b.configure(text=s)
    for b, s in zip(wednesday_buttons, status_list[28:42]):
        if s == "X":
            b.configure(text=s)
    for b, s in zip(thursday_buttons, status_list[42:56]):
        if s == "X":
            b.configure(text=s)
    for b, s in zip(friday_buttons, status_list[56:70]):
        if s == "X":
            b.configure(text=s)
    for b, s in zip(saturday_buttons, status_list[70:84]):
        if s == "X":
            b.configure(text=s)
    for b, s in zip(sunday_buttons, status_list[84:98]):
        if s == "X":
            b.configure(text=s)


def get_button_status():
    global btn_status_list

    btn_status_list = []

    for group in btn_list:
        for btn in group:
            btn_status_list.append(btn["text"][:])


# Clear Scheduler Ask
def clear_scheduler_ask():
    """
    Ask the user, then clear all scheduler buttons, lecture info, reset filters and the navigator
    :return: None
    """
    if messagebox.askokcancel("Clear All", "Do you want to clear?"):
        clear_scheduler()

        print("CLEAR ALL SCHEDULER")
        print("\n---------------------------------------------------------------------\n")


# Clear Scheduler
def clear_scheduler():
    """
    Clear all scheduler buttons, lecture info, reset filters and the navigator
    :return: None
    """
    global teacher_blacklist, section_blacklist
    global old_comb, current_comb, current_comb_num

    delete_lecture_id_buttons()
    delete_lecture_info_buttons()
    reset_scheduler_buttons()
    clear_filters()
    reset_data()
    reset_undo_redo()
    nav_info.set("0/0")


def reset_data():
    global old_comb, current_comb, current_comb_num
    global teacher_blacklist, section_blacklist
    global all_combinations, valid_combinations

    all_combinations, valid_combinations = [], []
    old_comb, current_comb, current_comb_num = [], [], -1
    teacher_blacklist, section_blacklist = [], []


# Import Semester
def import_semester():
    """
    Ask the user to open semester lecture info file (.json)
    :return: None
    """
    global lecture_dict

    try:
        filename = askopenfile(defaultextension=".json", filetypes=(("JSON Files", "*.json"), ("All files", "*.*")))

        program = str(filename).rsplit("/", 1)[1]
        if "lecture" in str(program):
            with open(filename.name, "r") as prog:
                lecture_dict = json.load(prog)

            for child in frame_course_code.winfo_children():
                child.destroy()

            clear_scheduler()
            create_course_code_buttons()

        else:
            raise IndexError

        print("Successful Semester Load!")
        print("\n---------------------------------------------------------------------\n")

        update_scheduler()

    except IndexError:
        print("Couldn't Load Semester! File name should contain 'lecture' in it!")
        print("\n---------------------------------------------------------------------\n")


# Export Semester
def export_semester():
    """
    Ask the user to save semester lecture info file (.json)
    :return: None
    """
    global lecture_dict

    try:
        filename = asksaveasfile(filetypes=(("JSON Files", "*.json"), ("All files", "*.*")), defaultextension=".json")
        with open(filename.name, 'w') as prog:
            json.dump(lecture_dict, prog)

    except IndexError:
        print("Couldn't Load Semester! File name should contain 'lecture' in it!")
        print("\n---------------------------------------------------------------------\n")


# Enable Scheduler Color
def enable_color():
    global color_switch
    color_switch = True
    print("COLOR SWITCHED TO ON\n")
    update_scheduler()


# Enable Scheduler Color
def disable_color():
    global color_switch
    color_switch = False
    print("COLOR SWITCHED TO OFF\n")
    update_scheduler()


# Main Win
root = tk.Tk()
root.title("Bilkent Program Scheduler Pandemic Edition by Can Gürsu")
root.configure(width=1400, height=800, bg="#D3D3D3")
root.iconbitmap("pencil_icon.ico")
root.minsize(1300, 650)

frame_background_color = "#FFFFFF"
frame_border_color = "#04080F"
bold = font.Font(weight="bold")

# Screen
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(root.winfo_screenheight() / 2.2 - windowHeight / 2)
root.geometry("+{}+{}".format(positionRight, positionDown))

# Course Code Frame
frame_course_code = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                             highlightthickness="2")
frame_course_code.place(relwidth=0.38, relheight=0.40, relx=0.01, rely=0.02)

# Lecture ID Frame
frame_lecture_id = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                            highlightthickness="2")
frame_lecture_id.place(relwidth=0.38, relheight=0.55, relx=0.01, rely=0.43)

# Scheduler Frame
frame_scheduler = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                           highlightthickness="2")
frame_scheduler.place(relwidth=0.59, relheight=0.6, relx=0.4, rely=0.02)

# Lecture Info Frame
frame_lecture_info = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                              highlightthickness="2")
frame_lecture_info.place(relwidth=0.2, relheight=0.35, relx=0.4, rely=0.63)

# Options Frame
frame_options = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                         highlightthickness="2")
frame_options.place(relwidth=0.09, relheight=0.35, relx=0.61, rely=0.63)

# Programs Frame
frame_programs = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                          highlightthickness="2")
frame_programs.place(relwidth=0.15, relheight=0.35, relx=0.84, rely=0.63)

# Program Frame Buttons
save = tk.Button(frame_programs, text="Save\nProgram", relief=tk.RAISED, command=save_program, font=bold)
save.place(relwidth=0.45, relheight=0.20, relx=0.05, rely=0.04)

load = tk.Button(frame_programs, text="Load\nProgram", relief=tk.RAISED, command=load_program, font=bold)
load.place(relwidth=0.45, relheight=0.20, relx=0.5, rely=0.04)

# Color Buttons
var = tk.IntVar()
color_on = tk.Radiobutton(frame_lecture_id, text="Color ON", variable=var, value=1, command=enable_color)
color_on.place(relwidth=0.20, relheight=0.04, relx=0.00, rely=0.96)
color_on.select()

color_off = tk.Radiobutton(frame_lecture_id, text="Color OFF", variable=var, value=2, command=disable_color)
color_off.place(relwidth=0.20, relheight=0.04, relx=0.21, rely=0.96)
color_switch = True


# Take screen shot
def screenshot():
    """
    Take a screenshot and ask the user for a name
    :return: None
    """
    file = asksaveasfile(mode='w', defaultextension=".png", filetypes=(("PNG Files", "*.png"), ("All files", "*.*")))
    if file:
        pyscreeze.screenshot(file.name)
    else:
        print("Couldn't Save!")


# Make full screen
def fullscreen():
    """
    Make the program full screen
    :return: None
    """
    root.attributes('-fullscreen', True)


# Make not full screen
def no_fullscreen():
    """
    Exit from full screen
    :return: None
    """
    root.attributes('-fullscreen', False)
    root.title("Bilkent Program Scheduler by Can Gürsu")


def fetch_data():
    global get_data_thread
    if messagebox.askyesno("Fetch New Data", "Your schedule might be deleted if you continue with this process. "
                                             "Be sure to save your schedule by pressing 'Save'. Do you wish to proceed?"
                           ):
        server_data["state"] = tk.DISABLED
        get_data_thread = threading.Thread(target=get_remote_data, )
        get_data_thread.start()


def get_remote_data():
    global lecture_dict
    global close_pogram
    try:
        response = requests.get("http://95.173.160.8:3103/get_data")

        lecture_dict = response.json()["lecture_dict"]
        # print(lecture_dict)

        for child in frame_course_code.winfo_children():
            child.destroy()

        clear_scheduler()
        create_course_code_buttons()

    except Exception:
        messagebox.showerror("Connection Error", "Couldn't get semester data, try again later")
        server_data["state"] = tk.NORMAL

    try:
        for _ in range(120):
            if close_program:
                raise Exception
            time.sleep(1)
        server_data["state"] = tk.NORMAL
    except Exception:
        pass


# Fullscreen/Screenshot Buttons
f_screen = tk.Button(frame_programs, text="Fullscreen", state=tk.NORMAL, relief=tk.RAISED, command=fullscreen)
f_screen.place(relwidth=0.45, relheight=0.20, relx=0.05, rely=0.55)

no_f_screen = tk.Button(frame_programs, text="No\nFullscreen", state=tk.NORMAL, relief=tk.RAISED, command=no_fullscreen)
no_f_screen.place(relwidth=0.45, relheight=0.20, relx=0.50, rely=0.55)

take_ss = tk.Button(frame_programs, text="Take Screenshot", state=tk.NORMAL, relief=tk.RAISED, command=screenshot)
take_ss.place(relwidth=0.9, relheight=0.20, relx=0.05, rely=0.76)

server_data = tk.Button(frame_programs, text="Fetch Semester Data", state=tk.NORMAL, relief=tk.RAISED, font=bold,
                        command=fetch_data)
server_data.place(relwidth=0.90, relheight=0.20, relx=0.05, rely=0.25)

# Navigator Frame
frame_navigator = tk.Frame(root, bg=frame_background_color, highlightbackground=frame_border_color,
                           highlightthickness="2")
frame_navigator.place(relwidth=0.12, relheight=0.35, relx=0.71, rely=0.63)

# Navigator Label
nav_info = tk.StringVar()
nav_info.set("0/0")
navigator = tk.Label(frame_navigator, textvariable=nav_info, relief=tk.SOLID, borderwidth="1", cursor="dotbox")
navigator.place(relwidth=0.495, relheight=0.195, relx=0.25, rely=0.04)

# Navigator Buttons
button_back = tk.Button(frame_navigator, text="<<", relief=tk.GROOVE, command=lambda: back(2))
button_back.place(relwidth=0.20, relheight=0.20, relx=0.05, rely=0.04)

button_forward = tk.Button(frame_navigator, text=">>", relief=tk.GROOVE, command=lambda: forward(2))
button_forward.place(relwidth=0.20, relheight=0.20, relx=0.75, rely=0.04)

# Undo/Redo Buttons
btn_undo = tk.Button(frame_navigator, text="Undo", relief=tk.RAISED, command=undo, state=tk.DISABLED, font=bold)
btn_undo.place(relwidth=0.45, relheight=0.20, relx=0.05, rely=0.35)

btn_redo = tk.Button(frame_navigator, text="Redo", relief=tk.RAISED, command=redo, state=tk.DISABLED, font=bold)
btn_redo.place(relwidth=0.45, relheight=0.20, relx=0.50, rely=0.35)

undo_redo_display = tk.StringVar()
undo_redo_display.set("")
u_r_disp_label = tk.Label(frame_navigator, textvariable=undo_redo_display, fg="red", relief=tk.FLAT, font=bold,
                          bg=frame_background_color)
u_r_disp_label.place(relwidth=1, relheight=0.10, relx=0, rely=0.56)

# Import Semester
btn_import_semester = tk.Button(frame_navigator, text="Import\nSemester", relief=tk.RAISED, command=import_semester)
btn_import_semester.place(relwidth=0.43, relheight=0.20, relx=0.07, rely=0.76)

# Export Semester
btn_export_semester = tk.Button(frame_navigator, text="Export\nSemester", relief=tk.RAISED, command=export_semester)
btn_export_semester.place(relwidth=0.43, relheight=0.20, relx=0.5, rely=0.76)


def delete_lecture_info_buttons():
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()


def current_lectures():
    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    return lecture_list


# Update Scheduler Frame
def update_scheduler():
    """
    Create global buttons, and assign lectures and colors to the buttons
    :return: None
    """

    for child in frame_scheduler.winfo_children():
        if child.winfo_class() == "Button":
            child.configure(fg="black")

    # Monday Buttons
    for index in range(14):
        if monday_buttons[index].cget("text") != "X":
            if index != 4:
                monday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                background=default_color,
                                                command=lambda btn_index=index: change_btn_status("mon", btn_index))
            else:
                monday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                background=default_color)
    # Tuesday Buttons
    for index in range(14):
        if tuesday_buttons[index].cget("text") != "X":
            if index != 4:
                tuesday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                 background=default_color,
                                                 command=lambda btn_index=index: change_btn_status("tue",
                                                                                                   btn_index))
            else:
                tuesday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                 background=default_color)
    # Wednesday Buttons
    for index in range(14):
        if wednesday_buttons[index].cget("text") != "X":
            if index != 4:
                wednesday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE,
                                                   activeforeground="red",
                                                   background=default_color,
                                                   command=lambda btn_index=index: change_btn_status("wed",
                                                                                                     btn_index))
            else:
                wednesday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE,
                                                   activeforeground="red",
                                                   background=default_color)
    # Thursday Buttons
    for index in range(14):
        if thursday_buttons[index].cget("text") != "X":
            if index != 4:
                thursday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                  background=default_color,
                                                  command=lambda btn_index=index: change_btn_status("thu",
                                                                                                    btn_index))
            else:
                thursday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                  background=default_color)
    # Friday Buttons
    for index in range(14):
        if friday_buttons[index].cget("text") != "X":
            if index != 4:
                friday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                background=default_color,
                                                command=lambda btn_index=index: change_btn_status("fri", btn_index))
            else:
                friday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                background=default_color)
    # Saturday Buttons
    for index in range(14):
        if saturday_buttons[index].cget("text") != "X":
            if index != 4:
                saturday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                  background=default_color,
                                                  command=lambda btn_index=index: change_btn_status("sat", btn_index))
            else:
                saturday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                  background=default_color)
    # Sunday Buttons
    for index in range(14):
        if sunday_buttons[index].cget("text") != "X":
            if index != 4:
                sunday_buttons[index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                background=default_color,
                                                command=lambda btn_index=index: change_btn_status("sun", btn_index))
            else:
                sunday_buttons[index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                background=default_color)

    random_colors = ["#35ba00", "#0026BF",
                     "#20A4F3", "#ff0033",
                     "#F28482", "#ffa500",
                     "#F497DA", "#694700"]

    print("Current Program Details:")
    for child in frame_lecture_info.winfo_children():
        btn_data = child.cget("text")
        c_code, rest = str(btn_data).split("-")
        c_name = str(c_code).split(" ")[0]
        c_section = str(rest).split(" ")[0]
        c_key = str(c_code) + "-" + str(c_section)
        c_hours = lecture_dict[c_name][c_key][1:len(lecture_dict[c_name][c_key])]
        print(btn_data)
        print("---->", c_hours)

        if c_hours[0] != "INVALID":
            color = random.choice(random_colors)
            random_colors.remove(color)

        for t in c_hours:
            # print(t)
            display = c_key
            if "[L]" in t:
                display += " [L]"
            elif "[S]" in t:
                display += " [S]"

            if t != "INVALID":
                day = t.split(" ")[0]
                specific_t = t.split(" ")[1]
                start, finish = specific_t.split("-")

                start_hour = int(start.split(":")[0])
                finish_hour = int(finish.split(":")[0])

                for h in range(start_hour, finish_hour):
                    if h == 12:
                        continue

                    # Monday
                    if "Mon" == day:
                        if h == 8:
                            monday_buttons[0]["text"] = display
                        elif h == 9:
                            monday_buttons[1]["text"] = display
                        elif h == 10:
                            monday_buttons[2]["text"] = display
                        elif h == 11:
                            monday_buttons[3]["text"] = display
                        elif h == 13:
                            monday_buttons[5]["text"] = display
                        elif h == 14:
                            monday_buttons[6]["text"] = display
                        elif h == 15:
                            monday_buttons[7]["text"] = display
                        elif h == 16:
                            monday_buttons[8]["text"] = display
                        elif h == 17:
                            monday_buttons[9]["text"] = display
                        elif h == 18:
                            monday_buttons[10]["text"] = display
                        elif h == 19:
                            monday_buttons[11]["text"] = display
                        elif h == 20:
                            monday_buttons[12]["text"] = display
                        elif h == 21:
                            monday_buttons[13]["text"] = display
                    # Tuesday
                    elif "Tue" == day:
                        if h == 8:
                            tuesday_buttons[0]["text"] = display
                        elif h == 9:
                            tuesday_buttons[1]["text"] = display
                        elif h == 10:
                            tuesday_buttons[2]["text"] = display
                        elif h == 11:
                            tuesday_buttons[3]["text"] = display
                        elif h == 13:
                            tuesday_buttons[5]["text"] = display
                        elif h == 14:
                            tuesday_buttons[6]["text"] = display
                        elif h == 15:
                            tuesday_buttons[7]["text"] = display
                        elif h == 16:
                            tuesday_buttons[8]["text"] = display
                        elif h == 17:
                            tuesday_buttons[9]["text"] = display
                        elif h == 18:
                            tuesday_buttons[10]["text"] = display
                        elif h == 19:
                            tuesday_buttons[11]["text"] = display
                        elif h == 20:
                            tuesday_buttons[12]["text"] = display
                        elif h == 21:
                            tuesday_buttons[13]["text"] = display
                    # Wednesday
                    elif "Wed" == day:
                        if h == 8:
                            wednesday_buttons[0]["text"] = display
                        elif h == 9:
                            wednesday_buttons[1]["text"] = display
                        elif h == 10:
                            wednesday_buttons[2]["text"] = display
                        elif h == 11:
                            wednesday_buttons[3]["text"] = display
                        elif h == 13:
                            wednesday_buttons[5]["text"] = display
                        elif h == 14:
                            wednesday_buttons[6]["text"] = display
                        elif h == 15:
                            wednesday_buttons[7]["text"] = display
                        elif h == 16:
                            wednesday_buttons[8]["text"] = display
                        elif h == 17:
                            wednesday_buttons[9]["text"] = display
                        elif h == 18:
                            wednesday_buttons[10]["text"] = display
                        elif h == 19:
                            wednesday_buttons[11]["text"] = display
                        elif h == 20:
                            wednesday_buttons[12]["text"] = display
                        elif h == 21:
                            wednesday_buttons[13]["text"] = display
                    # Thursday
                    elif "Thu" == day:
                        if h == 8:
                            thursday_buttons[0]["text"] = display
                        elif h == 9:
                            thursday_buttons[1]["text"] = display
                        elif h == 10:
                            thursday_buttons[2]["text"] = display
                        elif h == 11:
                            thursday_buttons[3]["text"] = display
                        elif h == 13:
                            thursday_buttons[5]["text"] = display
                        elif h == 14:
                            thursday_buttons[6]["text"] = display
                        elif h == 15:
                            thursday_buttons[7]["text"] = display
                        elif h == 16:
                            thursday_buttons[8]["text"] = display
                        elif h == 17:
                            thursday_buttons[9]["text"] = display
                        elif h == 18:
                            thursday_buttons[10]["text"] = display
                        elif h == 19:
                            thursday_buttons[11]["text"] = display
                        elif h == 20:
                            thursday_buttons[12]["text"] = display
                        elif h == 21:
                            thursday_buttons[13]["text"] = display
                    # Friday
                    elif "Fri" == day:
                        if h == 8:
                            friday_buttons[0]["text"] = display
                        elif h == 9:
                            friday_buttons[1]["text"] = display
                        elif h == 10:
                            friday_buttons[2]["text"] = display
                        elif h == 11:
                            friday_buttons[3]["text"] = display
                        elif h == 13:
                            friday_buttons[5]["text"] = display
                        elif h == 14:
                            friday_buttons[6]["text"] = display
                        elif h == 15:
                            friday_buttons[7]["text"] = display
                        elif h == 16:
                            friday_buttons[8]["text"] = display
                        elif h == 17:
                            friday_buttons[9]["text"] = display
                        elif h == 18:
                            friday_buttons[10]["text"] = display
                        elif h == 19:
                            friday_buttons[11]["text"] = display
                        elif h == 20:
                            friday_buttons[12]["text"] = display
                        elif h == 21:
                            friday_buttons[13]["text"] = display
                    # Saturday
                    elif "Sat" == day:
                        if h == 8:
                            saturday_buttons[0]["text"] = display
                        elif h == 9:
                            saturday_buttons[1]["text"] = display
                        elif h == 10:
                            saturday_buttons[2]["text"] = display
                        elif h == 11:
                            saturday_buttons[3]["text"] = display
                        elif h == 13:
                            saturday_buttons[5]["text"] = display
                        elif h == 14:
                            saturday_buttons[6]["text"] = display
                        elif h == 15:
                            saturday_buttons[7]["text"] = display
                        elif h == 16:
                            saturday_buttons[8]["text"] = display
                        elif h == 17:
                            saturday_buttons[9]["text"] = display
                        elif h == 18:
                            saturday_buttons[10]["text"] = display
                        elif h == 19:
                            saturday_buttons[11]["text"] = display
                        elif h == 20:
                            saturday_buttons[12]["text"] = display
                        elif h == 21:
                            saturday_buttons[13]["text"] = display
                    # Sunday
                    elif "Sun" == day:
                        if h == 8:
                            sunday_buttons[0]["text"] = display
                        elif h == 9:
                            sunday_buttons[1]["text"] = display
                        elif h == 10:
                            sunday_buttons[2]["text"] = display
                        elif h == 11:
                            sunday_buttons[3]["text"] = display
                        elif h == 13:
                            sunday_buttons[5]["text"] = display
                        elif h == 14:
                            sunday_buttons[6]["text"] = display
                        elif h == 15:
                            sunday_buttons[7]["text"] = display
                        elif h == 16:
                            sunday_buttons[8]["text"] = display
                        elif h == 17:
                            sunday_buttons[9]["text"] = display
                        elif h == 18:
                            sunday_buttons[10]["text"] = display
                        elif h == 19:
                            sunday_buttons[11]["text"] = display
                        elif h == 20:
                            sunday_buttons[12]["text"] = display
                        elif h == 21:
                            sunday_buttons[13]["text"] = display

        if color_switch is True:
            for btn in frame_scheduler.winfo_children():
                if btn.winfo_class() == "Button" and c_code in btn.cget("text"):
                    btn.configure(fg=color)
    print("\n---------------------------------------------------------------------\n")


# Change Button Status
def change_btn_status(day, btn_index):
    """
    Change button status of 'btn_name', fetch all lecture data in Lecture Information Frame,
    create a list with the lecture data (lec_list), and call available_course(lec_list).
    After that call update_scheduler() and update the Scheduler Frame
    :param day:
    :param btn_index:
    :return: None
    """

    global current_comb_num

    if day == "mon":
        if monday_buttons[btn_index].cget("text") == "X":
            monday_buttons[btn_index]["text"] = "__"
        else:
            monday_buttons[btn_index]["text"] = "X"
            monday_buttons[btn_index].configure(fg="black")

    if day == "tue":
        if tuesday_buttons[btn_index].cget("text") == "X":
            tuesday_buttons[btn_index]["text"] = "__"
        else:
            tuesday_buttons[btn_index]["text"] = "X"
            tuesday_buttons[btn_index].configure(fg="black")

    if day == "wed":
        if wednesday_buttons[btn_index].cget("text") == "X":
            wednesday_buttons[btn_index]["text"] = "__"
        else:
            wednesday_buttons[btn_index]["text"] = "X"
            wednesday_buttons[btn_index].configure(fg="black")

    if day == "thu":
        if thursday_buttons[btn_index].cget("text") == "X":
            thursday_buttons[btn_index]["text"] = "__"
        else:
            thursday_buttons[btn_index]["text"] = "X"
            thursday_buttons[btn_index].configure(fg="black")

    if day == "fri":
        if friday_buttons[btn_index].cget("text") == "X":
            friday_buttons[btn_index]["text"] = "__"
        else:
            friday_buttons[btn_index]["text"] = "X"
            friday_buttons[btn_index].configure(fg="black")

    if day == "sat":
        if saturday_buttons[btn_index].cget("text") == "X":
            saturday_buttons[btn_index]["text"] = "__"
        else:
            saturday_buttons[btn_index]["text"] = "X"
            saturday_buttons[btn_index].configure(fg="black")

    if day == "sun":
        if sunday_buttons[btn_index].cget("text") == "X":
            sunday_buttons[btn_index]["text"] = "__"
        else:
            sunday_buttons[btn_index]["text"] = "X"
            sunday_buttons[btn_index].configure(fg="black")

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    delete_lecture_info_buttons()

    find_combination_number()

    # Display
    print("STATUS CHANGE")
    display_combs()

    update_scheduler()
    extend_undo_redo()


# Change Day Status To Unavailable
def change_day_status(day):
    """
    Make the whole day available/ not available
    :param day:
    :return: None
    """

    global current_comb_num

    if str(day) == "0":
        busy_day = True
        for button in monday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                monday_buttons[i].configure(text="X", fg="black")
            else:
                monday_buttons[i].configure(text="__", fg="black")

    elif str(day) == "1":
        busy_day = True
        for button in tuesday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                tuesday_buttons[i].configure(text="X", fg="black")
            else:
                tuesday_buttons[i].configure(text="__", fg="black")

    elif str(day) == "2":
        busy_day = True
        for button in wednesday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                wednesday_buttons[i].configure(text="X", fg="black")
            else:
                wednesday_buttons[i].configure(text="__", fg="black")

    elif str(day) == "3":
        busy_day = True
        for button in thursday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                thursday_buttons[i].configure(text="X", fg="black")
            else:
                thursday_buttons[i].configure(text="__", fg="black")

    elif str(day) == "4":
        busy_day = True
        for button in friday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                friday_buttons[i].configure(text="X", fg="black")
            else:
                friday_buttons[i].configure(text="__", fg="black")

    elif str(day) == "5":
        busy_day = True
        for button in saturday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                saturday_buttons[i].configure(text="X", fg="black")
            else:
                saturday_buttons[i].configure(text="__", fg="black")

    elif str(day) == "6":
        busy_day = True
        for button in sunday_buttons:
            if button["text"] == "__":
                busy_day = False
                break

        for i in range(14):
            if i == 4:
                continue
            if not busy_day:
                sunday_buttons[i].configure(text="X", fg="black")
            else:
                sunday_buttons[i].configure(text="__", fg="black")

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append(
                [l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    delete_lecture_info_buttons()

    find_combination_number()

    # Display
    print("DAY {} STATUS CHANGE".format(day))
    display_combs()

    update_scheduler()
    extend_undo_redo()


# Change Hour Status
def change_hour_status(h):
    """
    Make all the same hours available/ not available
    :param h:
    :return: None
    """
    global current_comb_num

    if str(h) == "08":
        busy_hour = True
        for day_list in btn_list:
            if day_list[0]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][0].configure(text="X", fg="black")
            else:
                btn_list[i][0].configure(text="__", fg="black")

    elif str(h) == "09":
        busy_hour = True
        for day_list in btn_list:
            if day_list[1]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][1].configure(text="X", fg="black")
            else:
                btn_list[i][1].configure(text="__", fg="black")

    elif str(h) == "10":
        busy_hour = True
        for day_list in btn_list:
            if day_list[2]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][2].configure(text="X", fg="black")
            else:
                btn_list[i][2].configure(text="__", fg="black")

    elif str(h) == "11":
        busy_hour = True
        for day_list in btn_list:
            if day_list[3]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][3].configure(text="X", fg="black")
            else:
                btn_list[i][3].configure(text="__", fg="black")

    elif str(h) == "13":
        busy_hour = True
        for day_list in btn_list:
            if day_list[5]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][5].configure(text="X", fg="black")
            else:
                btn_list[i][5].configure(text="__", fg="black")

    elif str(h) == "14":
        busy_hour = True
        for day_list in btn_list:
            if day_list[6]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][6].configure(text="X", fg="black")
            else:
                btn_list[i][6].configure(text="__", fg="black")

    elif str(h) == "15":
        busy_hour = True
        for day_list in btn_list:
            if day_list[7]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][7].configure(text="X", fg="black")
            else:
                btn_list[i][7].configure(text="__", fg="black")

    elif str(h) == "16":
        busy_hour = True
        for day_list in btn_list:
            if day_list[8]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][8].configure(text="X", fg="black")
            else:
                btn_list[i][8].configure(text="__", fg="black")

    elif str(h) == "17":
        busy_hour = True
        for day_list in btn_list:
            if day_list[9]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][9].configure(text="X", fg="black")
            else:
                btn_list[i][9].configure(text="__", fg="black")

    elif str(h) == "18":
        busy_hour = True
        for day_list in btn_list:
            if day_list[10]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][10].configure(text="X", fg="black")
            else:
                btn_list[i][10].configure(text="__", fg="black")

    elif str(h) == "19":
        busy_hour = True
        for day_list in btn_list:
            if day_list[11]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][11].configure(text="X", fg="black")
            else:
                btn_list[i][11].configure(text="__", fg="black")

    elif str(h) == "20":
        busy_hour = True
        for day_list in btn_list:
            if day_list[12]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][12].configure(text="X", fg="black")
            else:
                btn_list[i][12].configure(text="__", fg="black")

    elif str(h) == "21":
        busy_hour = True
        for day_list in btn_list:
            if day_list[13]["text"] == "__":
                busy_hour = False
                break

        for i in range(7):
            if not busy_hour:
                btn_list[i][13].configure(text="X", fg="black")
            else:
                btn_list[i][13].configure(text="__", fg="black")

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    delete_lecture_info_buttons()

    find_combination_number()

    # Display
    print("HOUR {} STATUS CHANGE".format(h))
    display_combs()

    update_scheduler()
    extend_undo_redo()


def find_combination_number():
    global current_comb_num
    global current_comb
    global old_comb
    if valid_combinations:
        try:
            if current_comb != old_comb:
                # print("old current is not new current")
                for c in range(len(valid_combinations)):
                    if current_comb[0] is valid_combinations[c][0]:
                        current_comb_num = c + 1
                        old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
                        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
                        # print("old current is not new current and exists")
                        break
                else:
                    # print("old current is not new current and does not exist")
                    nav_info.set("1/" + str(len(valid_combinations)))
                    current_comb_num = 1
                    old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]
            else:
                # print("old current is new current")
                nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
        except IndexError:
            # print("old current is not new current and does not exist error")
            nav_info.set("1/" + str(len(valid_combinations)))
            current_comb_num = 1
            old_comb, current_comb = current_comb, valid_combinations[current_comb_num - 1]

        for l in list(valid_combinations[current_comb_num - 1]):
            # print(current_comb_num)
            # print(l)
            c_code, c_section = str(l).split("-")
            c_name = str(c_code).split(" ")[0]
            c_key = str(c_code) + "-" + str(c_section)

            course_teacher = lecture_dict[c_name][c_key][0]
            # print(c_code, c_section, course_teacher)
            # c_hours = lecture_dict[c_name][c_key][1:len(lecture_dict[c_name][c_key])]
            # print(c_hours)

            # Frame Lecture Info
            lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1], c_section,
                                                 course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_lecture_from_scheduler(l_info)).pack(side=tk.TOP,
                                                                                                      fill=tk.X)
    else:
        nav_info.set("0/0")
        old_comb, current_comb, current_comb_num = [], [], -1


# Course Frame Buttons
def create_course_code_buttons():
    """
    Create 'Course Code' buttons
    :return: None
    """
    relx_counter = 0.05  # Starting x pos
    rely_counter = 0.09  # Starting y pos
    max_course_col = 9
    course_col = 0
    for course in lecture_dict.keys():
        tk.Button(frame_course_code, text=course, padx=20, pady=10, command=lambda c=course: add_lecture_id_buttons(c))\
            .place(relwidth=0.1, relheight=0.1, relx=relx_counter, rely=rely_counter)

        course_col += 1
        relx_counter += 0.1

        if course_col == max_course_col:
            rely_counter += 0.1
            relx_counter = 0.05
            course_col = 0


def delete_course_code_buttons():
    for child in frame_course_code.winfo_children():
        if child.winfo_class() == 'Button':
            child.destroy()


# Scheduler Frame Day Buttons
def create_day_buttons():
    """
    Create Scheduler Frame 'day' buttons
    :return: None
    """
    day_relx_counter = 0.19
    day_rely_counter = 0.05

    day_btn = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE, font=bold,
                        activeforeground="red")

    day_btn.place(relwidth=0.15, relheight=0.06, relx=0.04, rely=day_rely_counter)

    day_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in range(7):
        day_btn = tk.Button(frame_scheduler, text=day_list[day], padx=20, pady=10, relief=tk.GROOVE, font=bold,
                            activeforeground="red", command=lambda d=day: change_day_status(d))

        day_btn.place(relwidth=0.11, relheight=0.06, relx=day_relx_counter, rely=day_rely_counter)

        day_relx_counter += 0.11


# Scheduler Frame Hour Buttons
def create_hour_buttons():
    """
    Create Scheduler Frame 'hour' buttons
    :return: None
    """
    hour_relx_counter = 0.04
    hour_rely_counter = 0.11
    hour_list = ["08:30", "09:30", "10:30", "11:30", "12:20 - (12:30)", "13:30", "14:30", "15:30", "16:20 - (16:30)",
                 "17:40 - (17:30)", "18:40 - (18:30)", "19:30", "20:10", "21:10"]
    for h in range(14):
        if hour_list[h] == "12:20":
            hour_btn = tk.Button(frame_scheduler, text=hour_list[h], padx=20, pady=10, relief=tk.GROOVE, font=bold,
                                 activeforeground="red")

            hour_btn.place(relwidth=0.15, relheight=0.06, relx=hour_relx_counter, rely=hour_rely_counter)

        else:
            hour_btn = tk.Button(frame_scheduler, text=hour_list[h], padx=20, pady=10, relief=tk.GROOVE,
                                 font=bold, activeforeground="red",
                                 command=lambda x=hour_list[h].split(":")[0]: change_hour_status(x))

            hour_btn.place(relwidth=0.15, relheight=0.06, relx=hour_relx_counter, rely=hour_rely_counter)

        hour_rely_counter += 0.06


# Initial Create Scheduler Buttons
def create_scheduler_buttons():
    global monday_buttons, tuesday_buttons, wednesday_buttons, thursday_buttons, friday_buttons, saturday_buttons, \
        sunday_buttons
    global default_color
    global btn_list

    btn_width = 0.11
    btn_height = 0.06

    # Monday Buttons
    monday_rel_x = 0.19
    monday_rel_y = 0.11
    monday_buttons = []
    for index in range(14):
        if index != 4:
            monday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                      activeforeground="red",
                                      command=lambda btn_index=index: change_btn_status("mon", btn_index))
        else:
            monday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                      activeforeground="red")
        monday_button.place(relwidth=btn_width, relheight=btn_height, relx=monday_rel_x, rely=monday_rel_y)
        monday_buttons.append(monday_button)
        monday_rel_y += 0.06

    # Tuesday Buttons
    tuesday_rel_x = 0.30
    tuesday_rel_y = 0.11
    tuesday_buttons = []
    for index in range(14):
        if index != 4:
            tuesday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                       activeforeground="red",
                                       command=lambda btn_index=index: change_btn_status("tue", btn_index))
        else:
            tuesday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                       activeforeground="red")
        tuesday_button.place(relwidth=btn_width, relheight=btn_height, relx=tuesday_rel_x, rely=tuesday_rel_y)
        tuesday_buttons.append(tuesday_button)
        tuesday_rel_y += 0.06

    # Wednesday Buttons
    wednesday_rel_x = 0.41
    wednesday_rel_y = 0.11
    wednesday_buttons = []
    for index in range(14):
        if index != 4:
            wednesday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                         activeforeground="red",
                                         command=lambda btn_index=index: change_btn_status("wed", btn_index))
        else:
            wednesday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                         activeforeground="red")
        wednesday_button.place(relwidth=btn_width, relheight=btn_height, relx=wednesday_rel_x, rely=wednesday_rel_y)
        wednesday_buttons.append(wednesday_button)
        wednesday_rel_y += 0.06

    # Thursday Buttons
    thursday_rel_x = 0.52
    thursday_rel_y = 0.11
    thursday_buttons = []
    for index in range(14):
        if index != 4:
            thursday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                        activeforeground="red",
                                        command=lambda btn_index=index: change_btn_status("thu", btn_index))
        else:
            thursday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                        activeforeground="red")
        thursday_button.place(relwidth=btn_width, relheight=btn_height, relx=thursday_rel_x, rely=thursday_rel_y)
        thursday_buttons.append(thursday_button)
        thursday_rel_y += 0.06

    # Friday Buttons
    friday_rel_x = 0.63
    friday_rel_y = 0.11
    friday_buttons = []
    for index in range(14):
        if index != 4:
            friday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                      activeforeground="red",
                                      command=lambda btn_index=index: change_btn_status("fri", btn_index))
        else:
            friday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                      activeforeground="red")
        friday_button.place(relwidth=btn_width, relheight=btn_height, relx=friday_rel_x, rely=friday_rel_y)
        friday_buttons.append(friday_button)
        friday_rel_y += 0.06

    # Saturday Buttons
    saturday_rel_x = 0.74
    saturday_rel_y = 0.11
    saturday_buttons = []
    for index in range(14):
        if index != 4:
            saturday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                        activeforeground="red",
                                        command=lambda btn_index=index: change_btn_status("sat", btn_index))
        else:
            saturday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                        activeforeground="red")
        saturday_button.place(relwidth=btn_width, relheight=btn_height, relx=saturday_rel_x, rely=saturday_rel_y)
        saturday_buttons.append(saturday_button)
        saturday_rel_y += 0.06

    # Sunday Buttons
    sunday_rel_x = 0.85
    sunday_rel_y = 0.11
    sunday_buttons = []
    for index in range(14):
        if index != 4:
            sunday_button = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE,
                                      activeforeground="red",
                                      command=lambda btn_index=index: change_btn_status("sun", btn_index))
        else:
            sunday_button = tk.Button(frame_scheduler, text="", padx=20, pady=10, relief=tk.GROOVE,
                                      activeforeground="red")
        sunday_button.place(relwidth=btn_width, relheight=btn_height, relx=sunday_rel_x, rely=sunday_rel_y)
        sunday_buttons.append(sunday_button)
        sunday_rel_y += 0.06

    btn_list = [monday_buttons, tuesday_buttons, wednesday_buttons, thursday_buttons, friday_buttons, saturday_buttons,
                sunday_buttons]
    default_color = monday_buttons[4].cget("background")


def reset_scheduler_buttons():
    day_list = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for group in range(5):
        for index in range(14):
            if index != 4:
                btn_list[group][index].configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                 fg="black",
                                                 command=lambda btn_index=index, group_index=group:
                                                 change_btn_status(day_list[group_index], btn_index))
            else:
                btn_list[group][index].configure(text="", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                                                 fg="black")


# Section Filter
def filter_section():
    """
    Create a new window, list all sections. When closed, the buttons which are red are put in a blacklist.
    Blacklisted sections are ignored in available_course()
    :return: None
    """
    global section_filter
    global frame_section_filter
    global section_canvas

    section_filter = tk.Toplevel()
    section_filter.title("Section Filter")
    section_filter.geometry("%dx%d%+d%+d" % (300, 500, 250, 125))
    section_filter.iconbitmap("pencil_icon.ico")
    section_filter.resizable(False, False)

    section_filter.grab_set()
    section_filter.focus_set()

    # Clear
    for child in section_filter.winfo_children():
        child.destroy()

    section_canvas = tk.Canvas(section_filter)
    section_scroll_y = tk.Scrollbar(section_filter, orient="vertical", command=section_canvas.yview)
    frame_section_filter = tk.Frame(section_canvas)

    no_lecture = True

    # Add Buttons
    for child in frame_lecture_info.winfo_children():
        def_lecture_info = child.cget("text")
        def_course_code, rest = str(def_lecture_info).split(" ")[0], str(def_lecture_info).split(" ")[1]
        def_lecture_code = rest.split("-")[0]
        def_lecture_id = str(def_course_code) + " " + str(def_lecture_code)

        section_list = []
        for l in lecture_dict[def_course_code].keys():
            if def_lecture_id in l:
                section_list.append(l)

        valid_sections = set([v for c in valid_combinations for l in c for v in section_list if v is l])

        # print(lecture_id)
        # print(section_list)
        # print(valid_sections)

        tk.Label(frame_section_filter, text=def_lecture_id, anchor=tk.W).pack(fill=tk.X)

        for s in section_list:
            if s in valid_sections:
                tk.Button(frame_section_filter, fg="green", text=s, command=lambda l_id=s: disable_section(l_id)) \
                    .pack(fill=tk.X)
            elif s in section_blacklist:
                tk.Button(frame_section_filter, fg="red", text=s, command=lambda l_id=s: enable_section(l_id)) \
                    .pack(fill=tk.X)
            else:
                tk.Button(frame_section_filter, text=s, state=tk.DISABLED).pack(fill=tk.X)
            no_lecture = False

        tk.Label(frame_section_filter, text="_______________________________________________________").pack(fill=tk.X)

    if no_lecture:
        tk.Label(frame_section_filter, text="No Sections to Filter!", fg="red").pack(fill=tk.X)
        tk.Label(frame_section_filter, text="_______________________________________________________").pack(fill=tk.X)

    section_canvas.create_window(0, 0, anchor='nw', window=frame_section_filter)
    section_canvas.update_idletasks()

    section_canvas.configure(scrollregion=section_canvas.bbox('all'), yscrollcommand=section_scroll_y.set)

    section_canvas.place(relwidth=0.95, relheight=1, relx=0, rely=0)
    section_scroll_y.place(relwidth=0.05, relheight=1, relx=0.95, rely=0)

    section_canvas.bind_all("<MouseWheel>", section_on_mousewheel)

    section_filter.protocol("WM_DELETE_WINDOW", close_section_filter)
    section_filter.mainloop()


# Disable Section
def disable_section(sec):
    """
    Make green(available) sections red(unavailable)
    :param sec:
    :return: None
    """
    # print("disable", sec)
    for child in frame_section_filter.winfo_children():
        if child.winfo_class() == "Button" and str(child.cget("text")) == str(sec):
            child.configure(fg="red", command=lambda l_id=sec: enable_section(sec))


# Enable Section
def enable_section(sec):
    """
    Make red(unavailable) sections green(available)
    :param sec:
    :return: None
    """
    # print("enable ", sec)
    for child in frame_section_filter.winfo_children():
        if child.winfo_class() == "Button" and str(child.cget("text")) == str(sec):
            child.configure(fg="green", command=lambda l_id=sec: disable_section(sec))


# Close Section Filter
def close_section_filter():
    """
    When closed, make the section_blacklist global, call available_courses() and update_scheduler()
    :return: None
    """
    global section_blacklist
    global current_comb_num
    section_blacklist = []
    for child in frame_section_filter.winfo_children():
        if child.winfo_class() == "Button" and child.cget("background") == "red":
            section_blacklist.append(str(child.cget("text")))
    section_canvas.unbind_all("<MouseWheel>")
    section_filter.destroy()

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    # print(lecture_list)
    available_course(lecture_list)

    delete_lecture_info_buttons()

    find_combination_number()

    print("SECTION FILTER\nBlacklisted Sections {}\n".format(section_blacklist))
    display_combs()

    update_scheduler()
    extend_undo_redo()


# Section Filter Mouse Wheel Bind
def section_on_mousewheel(event):
    """
    Bind the scrolling event of section_canvas to section_filter_scroll
    :param event:
    :return: None
    """
    section_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# Teacher Filter
def filter_teacher():
    """
    Create a new window, list all teachers. When closed, the buttons which are red are put in a blacklist.
    Blacklisted teachers are ignored in available_course()
    :return: None
    """
    global teacher_filter
    global frame_teacher_filter
    global teacher_canvas

    teacher_filter = tk.Toplevel()
    teacher_filter.title("Teacher Filter")
    teacher_filter.geometry("%dx%d%+d%+d" % (300, 500, 250, 125))
    teacher_filter.iconbitmap("pencil_icon.ico")
    teacher_filter.resizable(False, False)

    teacher_filter.grab_set()
    teacher_filter.focus_set()

    # Clear
    for child in teacher_filter.winfo_children():
        child.destroy()

    teacher_canvas = tk.Canvas(teacher_filter)
    teacher_scroll_y = tk.Scrollbar(teacher_filter, orient="vertical", command=teacher_canvas.yview)
    frame_teacher_filter = tk.Frame(teacher_canvas)

    no_lecture = True

    # Add Buttons
    for child in frame_lecture_info.winfo_children():
        lecture_info = child.cget("text")
        def_course_code, rest = str(lecture_info).split(" ")[0], str(lecture_info).split(" ")[1]
        lecture_code = rest.split("-")[0]
        def_lecture_id = str(def_course_code) + " " + str(lecture_code)

        teacher_list = []
        for l in lecture_dict[def_course_code].keys():
            if def_lecture_id in l:
                teacher_name = str(def_lecture_id) + "-" + str(lecture_dict[def_course_code][l][0])
                teacher_list.append(teacher_name)

        valid_teachers = []
        for c in valid_combinations:
            for l in c:
                for tl in teacher_list:
                    if lecture_dict[str(l).split(" ")[0]][l][0] in tl:
                        valid_teachers.append(tl)

        teacher_list = list(set(teacher_list))
        valid_teachers = set(valid_teachers)

        tk.Label(frame_teacher_filter, text=def_lecture_id, anchor=tk.W).pack(fill=tk.X)

        for t in teacher_list:
            if t in valid_teachers:
                tk.Button(frame_teacher_filter, fg="green", text=t, command=lambda l_id=t: disable_teacher(l_id)) \
                    .pack(fill=tk.X)
            elif t in teacher_blacklist:
                tk.Button(frame_teacher_filter, fg="red", text=t, command=lambda l_id=t: enable_teacher(l_id)) \
                    .pack(fill=tk.X)
            else:
                tk.Button(frame_teacher_filter, text=t, state=tk.DISABLED).pack(fill=tk.X)
            no_lecture = False

        tk.Label(frame_teacher_filter, text="_______________________________________________________").pack(fill=tk.X)

    if no_lecture:
        tk.Label(frame_teacher_filter, text="No Teachers to Filter!", fg="red").pack(fill=tk.X)
        tk.Label(frame_teacher_filter, text="_______________________________________________________").pack(fill=tk.X)

    teacher_canvas.create_window(0, 0, anchor='nw', window=frame_teacher_filter)
    teacher_canvas.update_idletasks()

    teacher_canvas.configure(scrollregion=teacher_canvas.bbox('all'), yscrollcommand=teacher_scroll_y.set)

    teacher_canvas.place(relwidth=0.95, relheight=1, relx=0, rely=0)
    teacher_scroll_y.place(relwidth=0.05, relheight=1, relx=0.95, rely=0)

    teacher_canvas.bind_all("<MouseWheel>", teacher_on_mousewheel)

    teacher_filter.protocol("WM_DELETE_WINDOW", close_teacher_filter)
    teacher_filter.mainloop()


# Disable Teacher
def disable_teacher(teach):
    """
    Make green(available) teachers red(unavailable)
    :param teach:
    :return: None
    """
    # print("disable", teach)
    for child in frame_teacher_filter.winfo_children():
        if child.winfo_class() == "Button" and str(child.cget("text")) == str(teach):
            child.configure(fg="red", command=lambda l_id=teach: enable_teacher(teach))


# Enable Teacher
def enable_teacher(teach):
    """
    Make red(unavailable) teachers green(available)
    :param teach:
    :return: None
    """
    # print("enable ", teach)
    for child in frame_teacher_filter.winfo_children():
        if child.winfo_class() == "Button" and str(child.cget("text")) == str(teach):
            child.configure(fg="green", command=lambda l_id=teach: disable_teacher(teach))


# Close Teacher Filter
def close_teacher_filter():
    """
    When closed, make the teacher_blacklist global, call available_courses() and update_scheduler()
    :return: None
    """
    global teacher_blacklist
    global current_comb_num
    teacher_blacklist = []
    for child in frame_teacher_filter.winfo_children():
        if child.winfo_class() == "Button" and child.cget("background") == "red":
            teacher_blacklist.append(str(child.cget("text")))
    teacher_canvas.unbind_all("<MouseWheel>")
    teacher_filter.destroy()

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    # print(lecture_list)
    available_course(lecture_list)

    delete_lecture_info_buttons()

    find_combination_number()

    print("TEACHER FILTER\nBlacklisted Teachers {}\n".format(teacher_blacklist))
    display_combs()

    update_scheduler()
    extend_undo_redo()


# Teacher Filter Mouse Wheel Bind
def teacher_on_mousewheel(event):
    """
    Bind the scrolling event of teacher_canvas to teacher_filter_scroll
    :param event:
    :return: None
    """
    teacher_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# Clear All Filters Ask
def clear_filters_ask():
    """
    Ask the user, then clear all filters
    :return: None
    """

    if messagebox.askokcancel("Clear Filters", "Do you want to clear the filters?"):
        print("CLEAR FILTERS\n")
        display_combs()

        clear_filters()


# Clear All Filters
def clear_filters():
    """
    Clear all filters
    :return: None
    """
    global teacher_blacklist
    global section_blacklist
    global current_comb_num

    teacher_blacklist, section_blacklist = [], []

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append(
                [l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    delete_lecture_info_buttons()

    reset_scheduler_buttons()

    find_combination_number()

    update_scheduler()


# Close Main Window
def close_main():
    global get_data_thread, close_program
    """
    Before the main window is closed, ask the user to confirm the exit
    :return: None
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        close_program = True
        try:
            get_data_thread.join()
        except NameError:
            pass


# Startup Functions
create_course_code_buttons()
create_day_buttons()
create_hour_buttons()
create_scheduler_buttons()
reset_data()
reset_undo_redo()

close_program = False

# Options Frame Buttons
s_filter = tk.Button(frame_options, text="Section\nFilter", relief=tk.RAISED, command=filter_section, font=bold)
s_filter.place(relwidth=0.84, relheight=0.20, relx=0.08, rely=0.04)

t_filter = tk.Button(frame_options, text="Teacher\nFilter", relief=tk.RAISED, command=filter_teacher, font=bold)
t_filter.place(relwidth=0.84, relheight=0.20, relx=0.08, rely=0.25)

btn_clear_filter = tk.Button(frame_options, text="Clear\nFilters", relief=tk.RAISED, command=clear_filters_ask,
                             font=bold)
btn_clear_filter.place(relwidth=0.84, relheight=0.20, relx=0.08, rely=0.46)

# Clear
clear = tk.Button(frame_options, text="Clear\nAll", relief=tk.RAISED, command=clear_scheduler_ask, font=bold)
clear.place(relwidth=0.84, relheight=0.20, relx=0.08, rely=0.76)

# Main Window Settings
root.bind('<Left>', lambda e: back(2))
root.bind('<Right>', lambda e: forward(2))
root.bind('<Escape>', lambda e: no_fullscreen())

root.protocol("WM_DELETE_WINDOW", close_main)
root.mainloop()
