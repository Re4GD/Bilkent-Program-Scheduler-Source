"""
    Bilkent Program Scheduler version 1.4.0 for Wındows
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

# TODO kesin gelecek programlar             TODO
# TODO total quota active quota             TODO
# TODO yazi boyutu kucult                   TODO

import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfile, asksaveasfile
import time
import pickle
import numpy as np
import itertools
import random
import pyautogui

try:
    with open("lectures.pckl", "rb") as f:
        lecture_dict = pickle.load(f)
        print("Data File Found!\n")
except FileNotFoundError:
    print("No Data File!\nPlease Select A Semester File!\n")
    lecture_dict = {}

"""
General Information About Courses/Lectures

# Course Code      : ME
# Lecture ID       : ME 232
# Lecture Code     : 232
# Lecture Section  : 1
# Lecture Full Name: ME 232-1
"""


# Timer
def timer(fnc):
    """
    A timer function to optimize available_course() and update_scheduler()
    :param fnc:
    :return: wrapper()
    """
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = fnc(*args, **kwargs)
        t2 = time.time() - t1
        print("{} ran in: {} sec".format(fnc.__name__, t2))
        return result
    return wrapper


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
def add_lec_ids(course_name):
    """
    Add Course Code buttons to Lecture ID Frame
    :param course_name:
    :return: None
    """
    # print(course_name)

    for child in frame_lecture_id.winfo_children():
        if child.winfo_class() == 'Button' or child.winfo_class() == 'Label':
            child.destroy()

    lecture_id_list = []

    try:
        for key in lecture_dict[course_name].keys():
            pos = key.find("-")
            key = key[:pos]
            if key not in lecture_id_list:
                lecture_id_list.append(key)

        # print(lecture_id_list)
        # print()

        # Course Buttons
        def_relx_counter = 0.05  # Starting x pos
        def_rely_counter = 0.05  # Starting y pos
        def_max_course_col = 6   # Max column number
        def_course_col = 0       # Column counter

        for lec_id in lecture_id_list:
            lec = tk.Button(frame_lecture_id, text=lec_id, padx=20, pady=10,
                            command=lambda l_id=lec_id: add_lec_to_scheduler(l_id))
            lec.place(relwidth=0.15, relheight=0.075, relx=def_relx_counter, rely=def_rely_counter)

            def_course_col += 1
            def_relx_counter += 0.15

            if def_course_col == def_max_course_col:
                def_rely_counter += 0.075
                def_relx_counter = 0.05
                def_course_col = 0

    except AttributeError:
        tk.Label(frame_lecture_id, text="NO LECTURE", fg="red").pack()


# Add Lecture Info and Update Scheduler
def add_lec_to_scheduler(course_name):
    """
    Add new course, call new_course(), add button for new course's information to Lecture Info Frame,
    and call update_scheduler() to update the Scheduler Frame
    :param course_name:
    :return: None
    """

    global update_lecture_name  # New lecture's name
    global current_comb_num  # Current combination number / also can be seen in the navigation bar

    current_comb_num = 1
    update_lecture_name = course_name

    # print(current_comb_num)

    lecture_info = tk.StringVar()

    # REFRESH
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button" and course_name in child.cget("text"):
            break
    else:
        new_course()

        for child in frame_lecture_info.winfo_children():
            if child.winfo_class() == "Button":
                child.destroy()

        if valid_combinations:
            # print(list(valid_combinations[current_comb_num - 1]))
            for l in reversed(list(valid_combinations[current_comb_num - 1])):
                # print(l)
                c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

                course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                # Display
                if str(c_name) in str(update_lecture_name):
                    print("ADDED\n{}-{} {}\n".format(c_name, c_section, course_teacher))

                    display_combs()

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                     c_section, course_teacher)
                # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

        update_scheduler()

    if not valid_combinations:
        nav_info.set("0/0")


# Delete Button when clicked
def delete_button(course_name):
    """
    Delete the course, call del_course(), delete course's information button from Lecture Info Frame,
    and update the Scheduler Frame
    :param course_name:
    :return: None
    """
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button" and course_name in str(child.cget("text")):
            # Display
            print("DELETED\n{}\n".format(child.cget("text")))
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

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    # print(valid_combinations)
    if valid_combinations:
        if valid_combinations[current_comb_num - 1]:
            for l in reversed(list(valid_combinations[current_comb_num - 1])):
                # print(l)
                c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

                course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                     c_section, course_teacher)
                # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

    update_scheduler()


# Add New Course
def new_course():
    """
    Look in the Lecture Information Frame, add the new course, fetch all lecture data,
    create a list with the lecture data (lec_list), and call available_course(lec_list)
    :return: None
    """
    global undo_redo_list
    global undo_redo_counter

    global btn_undo
    global btn_redo

    lecture_list = []

    new_lecture_id = str(update_lecture_name)
    new_course_code, new_lecture_code = str(new_lecture_id).split(" ")
    lecture_list.append([l for l in lecture_dict[new_course_code].keys()
                         if new_course_code + " " + new_lecture_code in l])
    # print(lecture_list)

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))                  # ME 232
            def_course_code = str(button_text).split(" ")[0]       # ME
            def_lecture_code = str(button_text).split(" ")[1][:3]  # 232
            if new_course_code + " " + new_lecture_code != def_course_code + " " + def_lecture_code:
                lecture_list.append([l for l in lecture_dict[def_course_code].keys()
                                     if def_course_code + " " + def_lecture_code in l])

    # print(lecture_list)
    available_course(lecture_list)

    # Undo/Redo
    undo_redo_display.set("")
    btn_redo["state"] = tk.DISABLED

    if len(undo_redo_list) == 1:
        btn_undo["state"] = tk.DISABLED
    else:
        btn_undo["state"] = tk.NORMAL

    undo_redo_counter += 1

    if len(undo_redo_list) - 1 != undo_redo_counter and undo_redo_counter >= 0:
        print("hi")
        undo_redo_list = undo_redo_list[:undo_redo_counter] + undo_redo_list[-1:]

    undo_redo_counter = len(undo_redo_list) - 1


# Delete New Course
def del_course():
    """
    Look in the Lecture Information Frame, delete the course, fetch all lecture data,
    create a list with the lecture data (lec_list), and call available_course(lec_list)
    :return: None
    """
    global undo_redo_list
    global undo_redo_counter

    global btn_undo
    global btn_redo

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    # print(lecture_list)
    available_course(lecture_list)

    # Undo/Redo
    undo_redo_display.set("")
    btn_redo["state"] = tk.DISABLED

    if len(undo_redo_list) == 1:
        btn_undo["state"] = tk.DISABLED
    else:
        btn_undo["state"] = tk.NORMAL

    undo_redo_counter += 1

    if len(undo_redo_list) - 1 != undo_redo_counter and undo_redo_counter >= 0:
        print("hi")
        undo_redo_list = undo_redo_list[:undo_redo_counter] + undo_redo_list[-1:]

    undo_redo_counter = len(undo_redo_list) - 1


# Find Available Courses
# @timer
def available_course(l_list):
    """
    Get the lecture list, and check the Scheduler Frame. Create valid programs,
    and make the valid_combinations list a global
    :param l_list:
    :return: None
    """
    global valid_combinations

    global all_combinations

    global current_comb
    global current_comb_num

    global btn_status_list

    global undo_redo_list
    global undo_redo_counter

    all_combinations = []
    valid_combinations = []

    if l_list:
        all_combinations = list(itertools.product(*l_list))

        for c in all_combinations:
            binary_list = np.zeros((8, 5))
            for l in c:
                course_binary = np.zeros((8, 5))
                def_course_code = l.split(" ")[0]
                for t in lecture_dict[def_course_code][l][1:len(lecture_dict[def_course_code])]:
                    # print(t)

                    if t != "INVALID":
                        specific_t = t.split(" ")[1]
                        start, finish = specific_t.split("-")

                        start_hour = str(start).split(":")[0]
                        finish_hour = str(finish).split(":")[0]

                        diff = int(finish_hour) - int(start_hour)

                        counter = int(start_hour)

                        for _ in range(diff):
                            n = "{}:40-{:02d}:30".format(counter, counter + 1)
                            # print(n)

                            # Monday
                            if "Mon" in t:
                                if "8:40-09:30" in n:
                                    if mon08.cget("text") != "X":
                                        course_binary[0][0] = 1
                                    else:
                                        course_binary[0][0] = 2

                                if "9:40-10:30" in n:
                                    if mon09.cget("text") != "X":
                                        course_binary[1][0] = 1
                                    else:
                                        course_binary[1][0] = 2

                                if "10:40-11:30" in n:
                                    if mon10.cget("text") != "X":
                                        course_binary[2][0] = 1
                                    else:
                                        course_binary[2][0] = 2

                                if "11:40-12:30" in n:
                                    if mon11.cget("text") != "X":
                                        course_binary[3][0] = 1
                                    else:
                                        course_binary[3][0] = 2

                                if "13:40-14:30" in n:
                                    if mon13.cget("text") != "X":
                                        course_binary[4][0] = 1
                                    else:
                                        course_binary[4][0] = 2

                                if "14:40-15:30" in n:
                                    if mon14.cget("text") != "X":
                                        course_binary[5][0] = 1
                                    else:
                                        course_binary[5][0] = 2

                                if "15:40-16:30" in n:
                                    if mon15.cget("text") != "X":
                                        course_binary[6][0] = 1
                                    else:
                                        course_binary[6][0] = 2

                                if "16:40-17:30" in n:
                                    if mon16.cget("text") != "X":
                                        course_binary[7][0] = 1
                                    else:
                                        course_binary[7][0] = 2

                            # Tuesday
                            if "Tue" in t:
                                if "8:40-09:30" in n:
                                    if tue08.cget("text") != "X":
                                        course_binary[0][1] = 1
                                    else:
                                        course_binary[0][1] = 2

                                if "9:40-10:30" in n:
                                    if tue09.cget("text") != "X":
                                        course_binary[1][1] = 1
                                    else:
                                        course_binary[1][1] = 2

                                if "10:40-11:30" in n:
                                    if tue10.cget("text") != "X":
                                        course_binary[2][1] = 1
                                    else:
                                        course_binary[2][1] = 2

                                if "11:40-12:30" in n:
                                    if tue11.cget("text") != "X":
                                        course_binary[3][1] = 1
                                    else:
                                        course_binary[3][1] = 2

                                if "13:40-14:30" in n:
                                    if tue13.cget("text") != "X":
                                        course_binary[4][1] = 1
                                    else:
                                        course_binary[4][1] = 2

                                if "14:40-15:30" in n:
                                    if tue14.cget("text") != "X":
                                        course_binary[5][1] = 1
                                    else:
                                        course_binary[5][1] = 2

                                if "15:40-16:30" in n:
                                    if tue15.cget("text") != "X":
                                        course_binary[6][1] = 1
                                    else:
                                        course_binary[6][1] = 2

                                if "16:40-17:30" in n:
                                    if tue16.cget("text") != "X":
                                        course_binary[7][1] = 1
                                    else:
                                        course_binary[7][1] = 2

                                if "8:40-10:30" in n:
                                    if (tue08.cget("text") is not "X") and (tue09.cget("text") is not "X"):
                                        course_binary[0][1], course_binary[1][1] = 1, 1
                                    else:
                                        course_binary[0][1], course_binary[1][1] = 2, 2

                            # Wednesday
                            if "Wed" in t:
                                if "8:40-09:30" in n:
                                    if wed08.cget("text") != "X":
                                        course_binary[0][2] = 1
                                    else:
                                        course_binary[0][2] = 2

                                if "9:40-10:30" in n:
                                    if wed09.cget("text") != "X":
                                        course_binary[1][2] = 1
                                    else:
                                        course_binary[1][2] = 2

                                if "10:40-11:30" in n:
                                    if wed10.cget("text") != "X":
                                        course_binary[2][2] = 1
                                    else:
                                        course_binary[2][2] = 2

                                if "11:40-12:30" in n:
                                    if wed11.cget("text") != "X":
                                        course_binary[3][2] = 1
                                    else:
                                        course_binary[3][2] = 2

                                if "13:40-14:30" in n:
                                    if wed13.cget("text") != "X":
                                        course_binary[4][2] = 1
                                    else:
                                        course_binary[4][2] = 2

                                if "14:40-15:30" in n:
                                    if wed14.cget("text") != "X":
                                        course_binary[5][2] = 1
                                    else:
                                        course_binary[5][2] = 2

                                if "15:40-16:30" in n:
                                    if wed15.cget("text") != "X":
                                        course_binary[6][2] = 1
                                    else:
                                        course_binary[6][2] = 2

                                if "16:40-17:30" in n:
                                    if wed16.cget("text") != "X":
                                        course_binary[7][2] = 1
                                    else:
                                        course_binary[7][2] = 2

                            # Thursday
                            if "Thu" in t:
                                if "8:40-09:30" in n:
                                    if thu08.cget("text") != "X":
                                        course_binary[0][3] = 1
                                    else:
                                        course_binary[0][3] = 2

                                if "9:40-10:30" in n:
                                    if thu09.cget("text") != "X":
                                        course_binary[1][3] = 1
                                    else:
                                        course_binary[1][3] = 2

                                if "10:40-11:30" in n:
                                    if thu10.cget("text") != "X":
                                        course_binary[2][3] = 1
                                    else:
                                        course_binary[2][3] = 2

                                if "11:40-12:30" in n:
                                    if thu11.cget("text") != "X":
                                        course_binary[3][3] = 1
                                    else:
                                        course_binary[3][3] = 2

                                if "13:40-14:30" in n:
                                    if thu13.cget("text") != "X":
                                        course_binary[4][3] = 1
                                    else:
                                        course_binary[4][3] = 2

                                if "14:40-15:30" in n:
                                    if thu14.cget("text") != "X":
                                        course_binary[5][3] = 1
                                    else:
                                        course_binary[5][3] = 2

                                if "15:40-16:30" in n:
                                    if thu15.cget("text") != "X":
                                        course_binary[6][3] = 1
                                    else:
                                        course_binary[6][3] = 2

                                if "16:40-17:30" in n:
                                    if thu16.cget("text") != "X":
                                        course_binary[7][3] = 1
                                    else:
                                        course_binary[7][3] = 2

                            # Friday
                            if "Fri" in t:
                                if "8:40-09:30" in n:
                                    if fri08.cget("text") != "X":
                                        course_binary[0][4] = 1
                                    else:
                                        course_binary[0][4] = 2

                                if "9:40-10:30" in n:
                                    if fri09.cget("text") != "X":
                                        course_binary[1][4] = 1
                                    else:
                                        course_binary[1][4] = 2

                                if "10:40-11:30" in n:
                                    if fri10.cget("text") != "X":
                                        course_binary[2][4] = 1
                                    else:
                                        course_binary[2][4] = 2

                                if "11:40-12:30" in n:
                                    if fri11.cget("text") != "X":
                                        course_binary[3][4] = 1
                                    else:
                                        course_binary[3][4] = 2

                                if "13:40-14:30" in n:
                                    if fri13.cget("text") != "X":
                                        course_binary[4][4] = 1
                                    else:
                                        course_binary[4][4] = 2

                                if "14:40-15:30" in n:
                                    if fri14.cget("text") != "X":
                                        course_binary[5][4] = 1
                                    else:
                                        course_binary[5][4] = 2

                                if "15:40-16:30" in n:
                                    if fri15.cget("text") != "X":
                                        course_binary[6][4] = 1
                                    else:
                                        course_binary[6][4] = 2

                                if "16:40-17:30" in n:
                                    if fri16.cget("text") != "X":
                                        course_binary[7][4] = 1
                                    else:
                                        course_binary[7][4] = 2

                            counter += 1

                # print(c)
                # print(l)
                # print(course_binary)

                # Section/Teacher Blacklist
                bl_teacher_found = False
                if teacher_blacklist:
                    for k in teacher_blacklist:
                        if lecture_dict[def_course_code][l][0] in k:
                            bl_teacher_found = True
                            break

                if l in section_blacklist or bl_teacher_found:
                    binary_list += 2 * course_binary
                else:
                    binary_list += course_binary

                # Optimization
                if (2 in binary_list) or (3 in binary_list) or (4 in binary_list) or (5 in binary_list):
                    break

            # print(binary_list)
            # print(c)

            binary_list = binary_list.astype(int)
            if (2 not in binary_list) and (3 not in binary_list) and (4 not in binary_list) and \
                    (5 not in binary_list) and (6 not in binary_list) and (7 not in binary_list):
                valid_combinations.append(c)
                # print(binary_list)

    if valid_combinations:
        nav_info.set("1/" + str(len(valid_combinations)))

        current_comb = valid_combinations[0]
        current_comb_num = 1
    else:
        nav_info.set("0/0")

    btn_status_list = [mon08["text"][:], mon09["text"][:], mon10["text"][:], mon11["text"][:], mon12["text"][:],
                       mon13["text"][:], mon14["text"][:], mon15["text"][:], mon16["text"][:],
                       tue08["text"][:], tue09["text"][:], tue10["text"][:], tue11["text"][:], tue12["text"][:],
                       tue13["text"][:], tue14["text"][:], tue15["text"][:], tue16["text"][:],
                       wed08["text"][:], wed09["text"][:], wed10["text"][:], wed11["text"][:], wed12["text"][:],
                       wed13["text"][:], wed14["text"][:], wed15["text"][:], wed16["text"][:],
                       thu08["text"][:], thu09["text"][:], thu10["text"][:], thu11["text"][:], thu12["text"][:],
                       thu13["text"][:], thu14["text"][:], thu15["text"][:], thu16["text"][:],
                       fri08["text"][:], fri09["text"][:], fri10["text"][:], fri11["text"][:], fri12["text"][:],
                       fri13["text"][:], fri14["text"][:], fri15["text"][:], fri16["text"][:]]

    undo_redo_list.append([all_combinations[:], valid_combinations[:], btn_status_list[:]])


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

    global current_comb
    global current_comb_num

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
        else:
            nav_info.set(str(next_num) + "/" + str(len(valid_combinations)))
            current_comb_num = next_num

        for child in frame_lecture_info.winfo_children():
            if child.winfo_class() == "Button":
                child.destroy()

        # Display
        print("NAVIGATE FORWARD\nNavigating to Combination {}\n".format(current_comb_num))
        display_combs()

        current_comb = valid_combinations[current_comb_num - 1]
        if valid_combinations:
            for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
                          command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
        else:
            nav_info.set("0/0")

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

    global current_comb
    global current_comb_num

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
        else:
            nav_info.set(str(next_num) + "/" + str(len(valid_combinations)))
            current_comb_num = next_num

        for child in frame_lecture_info.winfo_children():
            if child.winfo_class() == "Button":
                child.destroy()

        # Display
        print("NAVIGATE BACK\nNavigating to Combination {}\n".format(current_comb_num))
        display_combs()

        current_comb = valid_combinations[current_comb_num - 1]
        if valid_combinations:
            for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
                          command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
        else:
            nav_info.set("0/0")

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

    global btn_status_list

    btn_status_list = [mon08["text"][:], mon09["text"][:], mon10["text"][:], mon11["text"][:], mon12["text"][:],
                       mon13["text"][:], mon14["text"][:], mon15["text"][:], mon16["text"][:],
                       tue08["text"][:], tue09["text"][:], tue10["text"][:], tue11["text"][:], tue12["text"][:],
                       tue13["text"][:], tue14["text"][:], tue15["text"][:], tue16["text"][:],
                       wed08["text"][:], wed09["text"][:], wed10["text"][:], wed11["text"][:], wed12["text"][:],
                       wed13["text"][:], wed14["text"][:], wed15["text"][:], wed16["text"][:],
                       thu08["text"][:], thu09["text"][:], thu10["text"][:], thu11["text"][:], thu12["text"][:],
                       thu13["text"][:], thu14["text"][:], thu15["text"][:], thu16["text"][:],
                       fri08["text"][:], fri09["text"][:], fri10["text"][:], fri11["text"][:], fri12["text"][:],
                       fri13["text"][:], fri14["text"][:], fri15["text"][:], fri16["text"][:]]

    # print(btn_status_list)

    try:
        filename = asksaveasfile(filetypes=(("Pickle Files", "*.pckl"), ("All files", "*.*")), defaultextension=".pckl")
        if "program" not in filename.name:
            raise AttributeError
        with open(filename.name, 'wb') as prog:
            pickle.dump([all_combinations, valid_combinations, current_comb_num, btn_status_list], prog)

        print("Successful Save!")
        print("\n---------------------------------------------------------------------\n")
        # print(all_combinations, valid_combinations, current_comb_num)

    except AttributeError:
        print("Couldn't Save! File name should contain 'program' in it!")
        print("\n---------------------------------------------------------------------\n")


# Load Program
def load_program():
    """
    Load 'all_combinations', 'valid_combinations', 'button_status' from a pickle file
    :return: None
    """
    global all_combinations
    global valid_combinations
    global current_comb_num

    global btn_status_list
    global btn_list

    global btn_undo
    global btn_redo
    global undo_redo_list
    global undo_redo_counter

    try:
        filename = askopenfile()
        program = str(filename).rsplit("/", 1)[1]
        if "program" in str(program):
            with open(filename.name, "rb") as prog:
                all_combinations, valid_combinations, current_comb_num, btn_status_list = pickle.load(prog)
        else:
            raise IndexError

        print("Successful Load!")
        print("\n---------------------------------------------------------------------\n")

        clear_scheduler()

        for l in valid_combinations[current_comb_num - 1]:
            c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]
            course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

            # Frame Lecture Info
            lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                 c_section, course_teacher)

            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

        # print(btn_list)
        # print(btn_status_list)

        for b, s in zip(btn_list, btn_status_list):
            if s == "X":
                b.configure(text=s)

        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))

        update_scheduler()

        undo_redo_list.append([all_combinations[:], valid_combinations[:], btn_status_list[:]])

        # Undo/Redo
        undo_redo_display.set("")
        btn_redo["state"] = tk.DISABLED

        if len(undo_redo_list) == 1:
            btn_undo["state"] = tk.DISABLED
        else:
            btn_undo["state"] = tk.NORMAL

        undo_redo_counter += 1

        if len(undo_redo_list) - 1 != undo_redo_counter and undo_redo_counter >= 0:
            undo_redo_list = undo_redo_list[:undo_redo_counter] + undo_redo_list[-1:]

        undo_redo_counter = len(undo_redo_list) - 1

    except IndexError:
        print("Couldn't Load! File name should contain 'program' in it!")
        print("\n---------------------------------------------------------------------\n")


# Undo
def undo():
    """
    Based on 'undo_redo_counter', go back to the previous program
    :return: None
    """
    global all_combinations
    global valid_combinations

    global undo_redo_list
    global undo_redo_counter
    global undo_redo_display

    global btn_status_list
    global btn_list

    clear_scheduler()

    # print("list", undo_redo_list)
    # print("list len", len(undo_redo_list))
    # print("counter", undo_redo_counter)
    if undo_redo_list:
        if undo_redo_counter != 0:
            undo_redo_counter -= 1
            all_combinations, valid_combinations, btn_status_list = undo_redo_list[undo_redo_counter]
            # print("counter after", undo_redo_counter)

            print("UNDO")
            undo_redo_display.set("")
            btn_redo["state"] = tk.NORMAL

        if undo_redo_counter == 0:
            undo_redo_display.set("NO UNDO'S LEFT")
            btn_undo["state"] = tk.DISABLED

        # print("all", all_combinations)
        # print("val", valid_combinations)
        try:
            if valid_combinations[0]:
                for l in valid_combinations[0]:
                    c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]
                    course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                    # Frame Lecture Info
                    lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                         c_section, course_teacher)

                    tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                              command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

                # print(btn_list)
                # print(btn_status_list)

                for b, s in zip(btn_list, btn_status_list):
                    if s == "X":
                        b.configure(text=s)

                nav_info.set("1/" + str(len(valid_combinations)))
        except IndexError:
            pass

    display_combs()

    update_scheduler()


# Redo
def redo():
    """
    Based on 'undo_redo_counter', go forward to the next program
    :return: None
    """
    global all_combinations
    global valid_combinations

    global undo_redo_list
    global undo_redo_counter
    global undo_redo_display

    global btn_status_list
    global btn_list

    clear_scheduler()

    # print("list", undo_redo_list)
    # print("list len", len(undo_redo_list))
    # print("cntr", undo_redo_counter)
    if undo_redo_list:
        if undo_redo_counter != len(undo_redo_list) - 1:
            undo_redo_counter += 1
            all_combinations, valid_combinations, btn_status_list = undo_redo_list[undo_redo_counter]
            # print("counter after", undo_redo_counter)

            print("REDO")
            undo_redo_display.set("")
            btn_undo["state"] = tk.NORMAL

        if undo_redo_counter == len(undo_redo_list) - 1:
            undo_redo_display.set("NO REDO'S LEFT")
            btn_redo["state"] = tk.DISABLED

        # print("all", all_combinations)
        # print("val", valid_combinations)
        try:
            if valid_combinations[0]:
                for l in valid_combinations[0]:
                    c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]
                    course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                    # Frame Lecture Info
                    lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                         c_section, course_teacher)

                    tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                              command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

                # print(btn_list)
                # print(btn_status_list)

                for b, s in zip(btn_list, btn_status_list):
                    if s == "X":
                        b.configure(text=s)

                nav_info.set("1/" + str(len(valid_combinations)))
        except IndexError:
            pass

    display_combs()

    update_scheduler()


# Change Semester
def change_semester():
    """
    Ask the user to open semester lecture info file (.pckl)
    :return: None
    """
    global lecture_dict

    try:
        filename = askopenfile()
        program = str(filename).rsplit("/", 1)[1]
        if "lecture" in str(program):
            with open(filename.name, "rb") as prog:
                lecture_dict = pickle.load(prog)

            for child in frame_course_code.winfo_children():
                child.destroy()

            create_course_code_buttons()

        else:
            raise IndexError

        print("Successful Semester Load!")
        print("\n---------------------------------------------------------------------\n")

        clear_all()

        update_scheduler()

    except IndexError:
        print("Couldn't Load Semester! File name should contain 'lecture' in it!")
        print("\n---------------------------------------------------------------------\n")


# Main Win
root = tk.Tk()
root.title("Bilkent Program Scheduler")
root.configure(width=1200, height=600)
root.iconbitmap("pencil_icon.ico")
root.minsize(1100, 500)


# Screen
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
positionDown = int(root.winfo_screenheight() / 2.2 - windowHeight / 2)
root.geometry("+{}+{}".format(positionRight, positionDown))

# Course Code Frame
frame_course_code = tk.Frame(root, bg="white", highlightbackground="grey", highlightthickness="2")
frame_course_code.place(relwidth=0.38, relheight=0.40, relx=0.01, rely=0.02)

# Lecture ID Frame
frame_lecture_id = tk.Frame(root, bg="white", highlightbackground="grey", highlightthickness="2")
frame_lecture_id.place(relwidth=0.38, relheight=0.55, relx=0.01, rely=0.43)

# Scheduler Frame
frame_scheduler = tk.Frame(root, bg="white", highlightbackground="grey", highlightthickness="2")
frame_scheduler.place(relwidth=0.59, relheight=0.6, relx=0.4, rely=0.02)

# Lecture Info Frame
frame_lecture_info = tk.Frame(root, bg="white", highlightbackground="grey", highlightthickness="2")
frame_lecture_info.place(relwidth=0.2, relheight=0.35, relx=0.4, rely=0.63)

# Options Frame
frame_options = tk.Frame(root, bg="white", highlightbackground="grey", highlightthickness="0")
frame_options.place(relwidth=0.09, relheight=0.35, relx=0.61, rely=0.63)


# Programs Frame
frame_programs = tk.Frame(root, bg="white", highlightbackground="grey", highlightthickness="0")
frame_programs.place(relwidth=0.15, relheight=0.35, relx=0.84, rely=0.63)

# Program Frame Buttons
save = tk.Button(frame_programs, text="Save Program", relief=tk.GROOVE, command=save_program)
save.place(relwidth=1, relheight=0.25, relx=0, rely=0)

load = tk.Button(frame_programs, text="Load Program", relief=tk.GROOVE, command=load_program)
load.place(relwidth=1, relheight=0.25, relx=0, rely=0.25)


def screenshot():
    """
    Take a screenshot and ask the user for a name
    :return: None
    """
    file = asksaveasfile(mode='w', defaultextension=".png", filetypes=(("PNG Files", "*.png"), ("All files", "*.*")))
    if file:
        pyautogui.screenshot(file.name)
    else:
        print("Couldn't Save!")


def fullscreen():
    """
    Make the program full screen
    :return: None
    """
    root.attributes('-fullscreen', True)


def no_fullscreen():
    """
    Exit from full screen
    :return: None
    """
    root.attributes('-fullscreen', False)


# Fullscreen/Screenshot Buttons
f_screen = tk.Button(frame_programs, text="Fullscreen", state=tk.NORMAL, relief=tk.GROOVE, command=fullscreen)
f_screen.place(relwidth=0.50, relheight=0.25, relx=0, rely=0.50)

no_f_screen = tk.Button(frame_programs, text="No Fullscreen", state=tk.NORMAL, relief=tk.GROOVE, command=no_fullscreen)
no_f_screen.place(relwidth=0.50, relheight=0.25, relx=0.50, rely=0.50)

take_ss = tk.Button(frame_programs, text="Take Screenshot", state=tk.NORMAL, relief=tk.GROOVE, command=screenshot)
take_ss.place(relwidth=1, relheight=0.25, relx=0, rely=0.75)


# Navigator Frame
frame_navigator = tk.Frame(root, bg="white", highlightbackground="black", highlightthickness="0")
frame_navigator.place(relwidth=0.12, relheight=0.35, relx=0.71, rely=0.63)

# Navigator Label
nav_info = tk.StringVar()
nav_info.set("0/0")
navigator = tk.Label(frame_navigator, textvariable=nav_info, relief=tk.SOLID, borderwidth="1", cursor="dotbox")
navigator.place(relwidth=0.495, relheight=0.248, relx=0.25, rely=0)

# Navigator Buttons
button_back = tk.Button(frame_navigator, text="<<", relief=tk.GROOVE, command=lambda: back(2))
button_back.place(relwidth=0.25, relheight=0.25, relx=0, rely=0)

button_forward = tk.Button(frame_navigator, text=">>", relief=tk.GROOVE, command=lambda: forward(2))
button_forward.place(relwidth=0.25, relheight=0.25, relx=0.75, rely=0)

# Undo/Redo Buttons
btn_undo = tk.Button(frame_navigator, text="Undo", relief=tk.GROOVE, command=undo, state=tk.DISABLED)
btn_undo.place(relwidth=0.50, relheight=0.25, relx=0, rely=0.25)

btn_redo = tk.Button(frame_navigator, text="Redo", relief=tk.GROOVE, command=redo, state=tk.DISABLED)
btn_redo.place(relwidth=0.50, relheight=0.25, relx=0.50, rely=0.25)

undo_redo_display = tk.StringVar()
undo_redo_display.set("")
u_r_disp_label = tk.Label(frame_navigator, textvariable=undo_redo_display, fg="red", relief=tk.FLAT)
u_r_disp_label.place(relwidth=1, relheight=0.25, relx=0, rely=0.50)

# Change Semester
btn_change_semester = tk.Button(frame_navigator, text="Change Semester", relief=tk.GROOVE, command=change_semester)
btn_change_semester.place(relwidth=1, relheight=0.25, relx=0, rely=0.75)


# Initial Create Scheduler Buttons
if True:
    btn_width = 0.15
    btn_height = 0.09

    # Monday Buttons
    mon_rel_x = 0.20
    if True:
        mon08 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon08))
        mon09 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon09))
        mon10 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon10))
        mon11 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon11))
        mon12 = tk.Button(frame_scheduler, text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon12))
        mon13 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon13))
        mon14 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon14))
        mon15 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon15))
        mon16 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                          command=lambda: change_btn_status(mon16))

        mon08.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.15)
        mon09.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.24)
        mon10.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.33)
        mon11.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.42)
        mon12.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.51)
        mon13.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.60)
        mon14.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.69)
        mon15.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.78)
        mon16.place(relwidth=btn_width, relheight=btn_height, relx=mon_rel_x, rely=0.87)

    # Tuesday Buttons
    tue_rel_x = 0.35
    if True:
        tue08 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue09 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue10 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue11 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue12 = tk.Button(frame_scheduler, text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue13 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue14 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue15 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        tue16 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")

        tue08.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.15)
        tue09.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.24)
        tue10.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.33)
        tue11.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.42)
        tue12.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.51)
        tue13.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.60)
        tue14.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.69)
        tue15.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.78)
        tue16.place(relwidth=btn_width, relheight=btn_height, relx=tue_rel_x, rely=0.87)

    # Wednesday Buttons
    wed_rel_x = 0.50
    if True:
        wed08 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed09 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed10 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed11 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed12 = tk.Button(frame_scheduler, text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed13 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed14 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed15 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        wed16 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")

        wed08.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.15)
        wed09.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.24)
        wed10.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.33)
        wed11.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.42)
        wed12.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.51)
        wed13.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.60)
        wed14.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.69)
        wed15.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.78)
        wed16.place(relwidth=btn_width, relheight=btn_height, relx=wed_rel_x, rely=0.87)

    # Thursday Buttons
    thu_rel_x = 0.65
    if True:
        thu08 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu09 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu10 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu11 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu12 = tk.Button(frame_scheduler, text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu13 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu14 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu15 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        thu16 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")

        thu08.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.15)
        thu09.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.24)
        thu10.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.33)
        thu11.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.42)
        thu12.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.51)
        thu13.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.60)
        thu14.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.69)
        thu15.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.78)
        thu16.place(relwidth=btn_width, relheight=btn_height, relx=thu_rel_x, rely=0.87)

    # Friday Buttons
    fri_rel_x = 0.80
    if True:
        fri08 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri09 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri10 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri11 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri12 = tk.Button(frame_scheduler, text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri13 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri14 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri15 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")
        fri16 = tk.Button(frame_scheduler, text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red")

        fri08.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.15)
        fri09.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.24)
        fri10.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.33)
        fri11.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.42)
        fri12.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.51)
        fri13.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.60)
        fri14.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.69)
        fri15.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.78)
        fri16.place(relwidth=btn_width, relheight=btn_height, relx=fri_rel_x, rely=0.87)

btn_list = [mon08, mon09, mon10, mon11, mon12, mon13, mon14, mon15, mon16,
            tue08, tue09, tue10, tue11, tue12, tue13, tue14, tue15, tue16,
            wed08, wed09, wed10, wed11, wed12, wed13, wed14, wed15, wed16,
            thu08, thu09, thu10, thu11, thu12, thu13, thu14, thu15, thu16,
            fri08, fri09, fri10, fri11, fri12, fri13, fri14, fri15, fri16]

default_color = mon12.cget("background")


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
    # Globals
    global teacher_blacklist
    global section_blacklist

    global all_combinations
    global valid_combinations

    if True:
        global mon08
        global mon09
        global mon10
        global mon11
        global mon12
        global mon13
        global mon14
        global mon15
        global mon16

        global tue08
        global tue09
        global tue10
        global tue11
        global tue12
        global tue13
        global tue14
        global tue15
        global tue16

        global wed08
        global wed09
        global wed10
        global wed11
        global wed12
        global wed13
        global wed14
        global wed15
        global wed16

        global thu08
        global thu09
        global thu10
        global thu11
        global thu12
        global thu13
        global thu14
        global thu15
        global thu16

        global fri08
        global fri09
        global fri10
        global fri11
        global fri12
        global fri13
        global fri14
        global fri15
        global fri16

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    # Monday Buttons
    if True:
        mon08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon08))
        mon09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon09))
        mon10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon10))
        mon11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon11))
        mon13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon13))
        mon14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon14))
        mon15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon15))
        mon16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon16))

    # Tuesday Buttons
    if True:
        tue08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue08))
        tue09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue09))
        tue10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue10))
        tue11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue11))
        tue13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue13))
        tue14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue14))
        tue15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue15))
        tue16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue16))

    # Wednesday Buttons
    if True:
        wed08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed08))
        wed09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed09))
        wed10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed10))
        wed11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed11))
        wed13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed13))
        wed14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed14))
        wed15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed15))
        wed16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed16))

    # Thursday Buttons
    if True:
        thu08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu08))
        thu09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu09))
        thu10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu10))
        thu11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu11))
        thu13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu13))
        thu14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu14))
        thu15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu15))
        thu16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu16))

    # Friday Buttons
    if True:
        fri08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri08))
        fri09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri09))
        fri10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri10))
        fri11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri11))
        fri13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri13))
        fri14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri14))
        fri15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri15))
        fri16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri16))

    nav_info.set("0/0")
    teacher_blacklist, section_blacklist = [], []


# Clear Scheduler Ask
def clear_all_ask():
    """
    Ask the user, then clear all scheduler buttons, lecture info, reset filters and the navigator, undo/redo stuff
    :return: None
    """
    if messagebox.askokcancel("Clear All", "Do you want to clear?"):
        clear_all()

        print("CLEAR ALL")
        print("\n---------------------------------------------------------------------\n")


# Clear All
def clear_all():
    """
    Clear all scheduler buttons, lecture info, reset filters and the navigator, undo/redo stuff
    :return: None
    """
    # Globals
    global undo_redo_list
    global undo_redo_counter
    global undo_redo_display

    global teacher_blacklist
    global section_blacklist

    if True:
        global mon08
        global mon09
        global mon10
        global mon11
        global mon12
        global mon13
        global mon14
        global mon15
        global mon16

        global tue08
        global tue09
        global tue10
        global tue11
        global tue12
        global tue13
        global tue14
        global tue15
        global tue16

        global wed08
        global wed09
        global wed10
        global wed11
        global wed12
        global wed13
        global wed14
        global wed15
        global wed16

        global thu08
        global thu09
        global thu10
        global thu11
        global thu12
        global thu13
        global thu14
        global thu15
        global thu16

        global fri08
        global fri09
        global fri10
        global fri11
        global fri12
        global fri13
        global fri14
        global fri15
        global fri16

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    # Monday Buttons
    if True:
        mon08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon08))
        mon09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon09))
        mon10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon10))
        mon11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon11))
        mon13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon13))
        mon14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon14))
        mon15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon15))
        mon16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(mon16))

    # Tuesday Buttons
    if True:
        tue08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue08))
        tue09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue09))
        tue10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue10))
        tue11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue11))
        tue13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue13))
        tue14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue14))
        tue15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue15))
        tue16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(tue16))

    # Wednesday Buttons
    if True:
        wed08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed08))
        wed09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed09))
        wed10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed10))
        wed11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed11))
        wed13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed13))
        wed14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed14))
        wed15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed15))
        wed16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(wed16))

    # Thursday Buttons
    if True:
        thu08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu08))
        thu09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu09))
        thu10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu10))
        thu11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu11))
        thu13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu13))
        thu14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu14))
        thu15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu15))
        thu16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(thu16))

    # Friday Buttons
    if True:
        fri08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri08))
        fri09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri09))
        fri10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri10))
        fri11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri11))
        fri13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri13))
        fri14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri14))
        fri15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri15))
        fri16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red", background=default_color,
                        command=lambda: change_btn_status(fri16))

    nav_info.set("0/0")
    teacher_blacklist, section_blacklist = [], []

    undo_redo_display.set("")
    btn_undo["state"] = tk.DISABLED
    btn_redo["state"] = tk.DISABLED

    undo_redo_list, undo_redo_counter = [], -1


# Update Scheduler Frame
# @timer
def update_scheduler():
    """
    Create global buttons, and assign lectures and colors to the buttons
    :return: None
    """
    # Globals
    if True:
        global mon08
        global mon09
        global mon10
        global mon11
        global mon12
        global mon13
        global mon14
        global mon15
        global mon16

        global tue08
        global tue09
        global tue10
        global tue11
        global tue12
        global tue13
        global tue14
        global tue15
        global tue16

        global wed08
        global wed09
        global wed10
        global wed11
        global wed12
        global wed13
        global wed14
        global wed15
        global wed16

        global thu08
        global thu09
        global thu10
        global thu11
        global thu12
        global thu13
        global thu14
        global thu15
        global thu16

        global fri08
        global fri09
        global fri10
        global fri11
        global fri12
        global fri13
        global fri14
        global fri15
        global fri16

    # Monday Buttons
    if True:
        if mon08.cget("text") is not "X":

            mon08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon08))

        if mon09.cget("text") is not "X":
            mon09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon09))

        if mon10.cget("text") is not "X":
            mon10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon10))

        if mon11.cget("text") is not "X":
            mon11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon11))

        if mon12.cget("text") is not "X":
            mon12.configure(text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon12))

        if mon13.cget("text") is not "X":
            mon13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon13))

        if mon14.cget("text") is not "X":
            mon14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon14))

        if mon15.cget("text") is not "X":
            mon15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon15))

        if mon16.cget("text") is not "X":
            mon16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(mon16))

    # Tuesday Buttons
    if True:
        if tue08.cget("text") is not "X":
            tue08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue08))
        if tue09.cget("text") is not "X":
            tue09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue09))
        if tue10.cget("text") is not "X":
            tue10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue10))
        if tue11.cget("text") is not "X":
            tue11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue11))
        if tue12.cget("text") is not "X":
            tue12.configure(text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue12))
        if tue13.cget("text") is not "X":
            tue13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue13))
        if tue14.cget("text") is not "X":
            tue14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue14))
        if tue15.cget("text") is not "X":
            tue15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue15))
        if tue16.cget("text") is not "X":
            tue16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(tue16))

    # Wednesday Buttons
    if True:
        if wed08.cget("text") is not "X":
            wed08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed08))
        if wed09.cget("text") is not "X":
            wed09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed09))
        if wed10.cget("text") is not "X":
            wed10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed10))
        if wed11.cget("text") is not "X":
            wed11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed11))
        if wed12.cget("text") is not "X":
            wed12.configure(text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed12))
        if wed13.cget("text") is not "X":
            wed13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed13))
        if wed14.cget("text") is not "X":
            wed14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed14))
        if wed15.cget("text") is not "X":
            wed15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed15))
        if wed16.cget("text") is not "X":
            wed16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(wed16))

    # Thursday Buttons
    if True:
        if thu08.cget("text") is not "X":
            thu08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu08))
        if thu09.cget("text") is not "X":
            thu09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu09))
        if thu10.cget("text") is not "X":
            thu10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu10))
        if thu11.cget("text") is not "X":
            thu11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu11))
        if thu12.cget("text") is not "X":
            thu12.configure(text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu12))
        if thu13.cget("text") is not "X":
            thu13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu13))
        if thu14.cget("text") is not "X":
            thu14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu14))
        if thu15.cget("text") is not "X":
            thu15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu15))
        if thu16.cget("text") is not "X":
            thu16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(thu16))

    # Friday Buttons
    if True:
        if fri08.cget("text") is not "X":
            fri08.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri08))
        if fri09.cget("text") is not "X":
            fri09.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri09))
        if fri10.cget("text") is not "X":
            fri10.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri10))
        if fri11.cget("text") is not "X":
            fri11.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri11))
        if fri12.cget("text") is not "X":
            fri12.configure(text="  ", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri12))
        if fri13.cget("text") is not "X":
            fri13.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri13))
        if fri14.cget("text") is not "X":
            fri14.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri14))
        if fri15.cget("text") is not "X":
            fri15.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri15))
        if fri16.cget("text") is not "X":
            fri16.configure(text="__", padx=20, pady=10, relief=tk.GROOVE, activeforeground="red",
                            background=default_color, command=lambda: change_btn_status(fri16))

    random_colors = ["#FF0000", "#F359F3", "#7A93F9", "#6CEF86", "#ffa500", "#00FFFF", "#ffff00", "#E0F76A"]

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
                specific_t = t.split(" ")[1]
                start, finish = specific_t.split("-")

                start_hour = str(start).split(":")[0]
                finish_hour = str(finish).split(":")[0]

                diff = int(finish_hour) - int(start_hour)

                counter = int(start_hour)

                for _ in range(diff):
                    n = "{}:40-{:02d}:30".format(counter, counter + 1)
                    # print(n)

                    # Monday
                    if "Mon" in t:
                        if "8:40-09:30" in n:
                            mon08["text"] = display
                        if "9:40-10:30" in n:
                            mon09["text"] = display
                        if "10:40-11:30" in n:
                            mon10["text"] = display
                        if "11:40-12:30" in n:
                            mon11["text"] = display
                        if "13:40-14:30" in n:
                            mon13["text"] = display
                        if "14:40-15:30" in n:
                            mon14["text"] = display
                        if "15:40-16:30" in n:
                            mon15["text"] = display
                        if "16:40-17:30" in n:
                            mon16["text"] = display

                    # Tuesday
                    if "Tue" in t:
                        if "8:40-09:30" in n:
                            tue08["text"] = display
                        if "9:40-10:30" in n:
                            tue09["text"] = display
                        if "10:40-11:30" in n:
                            tue10["text"] = display
                        if "11:40-12:30" in n:
                            tue11["text"] = display
                        if "13:40-14:30" in n:
                            tue13["text"] = display
                        if "14:40-15:30" in n:
                            tue14["text"] = display
                        if "15:40-16:30" in n:
                            tue15["text"] = display
                        if "16:40-17:30" in n:
                            tue16["text"] = display

                    # Wednesday
                    if "Wed" in t:
                        if "8:40-09:30" in n:
                            wed08["text"] = display
                        if "9:40-10:30" in n:
                            wed09["text"] = display
                        if "10:40-11:30" in n:
                            wed10["text"] = display
                        if "11:40-12:30" in n:
                            wed11["text"] = display
                        if "13:40-14:30" in n:
                            wed13["text"] = display
                        if "14:40-15:30" in n:
                            wed14["text"] = display
                        if "15:40-16:30" in n:
                            wed15["text"] = display
                        if "16:40-17:30" in n:
                            wed16["text"] = display

                    # Thursday
                    if "Thu" in t:
                        if "8:40-09:30" in n:
                            thu08["text"] = display
                        if "9:40-10:30" in n:
                            thu09["text"] = display
                        if "10:40-11:30" in n:
                            thu10["text"] = display
                        if "11:40-12:30" in n:
                            thu11["text"] = display
                        if "13:40-14:30" in n:
                            thu13["text"] = display
                        if "14:40-15:30" in n:
                            thu14["text"] = display
                        if "15:40-16:30" in n:
                            thu15["text"] = display
                        if "16:40-17:30" in n:
                            thu16["text"] = display

                    # Friday
                    if "Fri" in t:
                        if "8:40-09:30" in n:
                            fri08["text"] = display
                        if "9:40-10:30" in n:
                            fri09["text"] = display
                        if "10:40-11:30" in n:
                            fri10["text"] = display
                        if "11:40-12:30" in n:
                            fri11["text"] = display
                        if "13:40-14:30" in n:
                            fri13["text"] = display
                        if "14:40-15:30" in n:
                            fri14["text"] = display
                        if "15:40-16:30" in n:
                            fri15["text"] = display
                        if "16:40-17:30" in n:
                            fri16["text"] = display

                    counter += 1

        for btn in frame_scheduler.winfo_children():
            if btn.winfo_class() == "Button" and c_code in btn.cget("text"):
                btn.configure(bg=color)
    print("\n---------------------------------------------------------------------\n")


# Change Button Status
def change_btn_status(btn_name):
    """
    Change button status of 'btn_name', fetch all lecture data in Lecture Information Frame,
    create a list with the lecture data (lec_list), and call available_course(lec_list).
    After that call update_scheduler() and update the Scheduler Frame
    :param btn_name:
    :return: None
    """
    global valid_combinations

    global current_comb
    global current_comb_num

    global undo_redo_list
    global undo_redo_counter
    global undo_redo_display

    global default_color

    if btn_name.cget("text") == "X":
        btn_name["text"] = "__"
        # print("Button {} AVAILABLE\n".format(btn_name))
    else:
        btn_name["text"] = "X"
        btn_name.configure(bg=default_color)
        # print("Button {} NOT AVAILABLE\n".format(btn_name))

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    # print(current_comb_num)
    # print("old", current_comb)
    # print("new", valid_combinations[current_comb_num - 1])

    # REUSED at filters
    if valid_combinations:
        try:
            if current_comb != valid_combinations[current_comb_num - 1]:
                # print("current is not new and might exist")
                for c in range(len(valid_combinations)):
                    if current_comb[0] is valid_combinations[c][0]:
                        current_comb_num = c + 1
                        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
                        # print("current is not new and exists")
                        break
                else:
                    # print("current is not new and no exist")
                    nav_info.set("1/" + str(len(valid_combinations)))
            else:
                # print("current is new")
                nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
        except IndexError:
            # print("current is not new and no exist error")
            current_comb_num = 1

        for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
            lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1], c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
    else:
        nav_info.set("0/0")

    # Display
    print("STATUS CHANGE")
    display_combs()

    update_scheduler()

    undo_redo_display.set("")
    btn_redo["state"] = tk.DISABLED

    if len(undo_redo_list) == 1:
        btn_undo["state"] = tk.DISABLED
    else:
        btn_undo["state"] = tk.NORMAL

    undo_redo_counter += 1

    if len(undo_redo_list) - 1 != undo_redo_counter and undo_redo_counter >= 0:
        undo_redo_list = undo_redo_list[:undo_redo_counter] + undo_redo_list[-1:]

    undo_redo_counter = len(undo_redo_list) - 1


# Change Day Status To Unavailable
def change_day_status(day):
    """
    Make the whole day available/ not available
    :param day:
    :return: None
    """
    global valid_combinations

    global current_comb
    global current_comb_num

    if str(day) == "1":
        if mon08["text"] is "X" and mon09["text"] is "X" and mon10["text"] is "X" and mon11["text"] is "X" and \
                mon13["text"] is "X" and mon14["text"] is "X" and mon15["text"] is "X" and mon16["text"] is "X":
            mon08.configure(text="_", bg=default_color)
            mon09.configure(text="_", bg=default_color)
            mon10.configure(text="_", bg=default_color)
            mon11.configure(text="_", bg=default_color)
            mon13.configure(text="_", bg=default_color)
            mon14.configure(text="_", bg=default_color)
            mon15.configure(text="_", bg=default_color)
            mon16.configure(text="_", bg=default_color)
        else:
            mon08.configure(text="X", bg=default_color)
            mon09.configure(text="X", bg=default_color)
            mon10.configure(text="X", bg=default_color)
            mon11.configure(text="X", bg=default_color)
            mon13.configure(text="X", bg=default_color)
            mon14.configure(text="X", bg=default_color)
            mon15.configure(text="X", bg=default_color)
            mon16.configure(text="X", bg=default_color)

    elif str(day) == "2":
        if tue08["text"] is "X" and tue09["text"] is "X" and tue10["text"] is "X" and tue11["text"] is "X" and \
                tue13["text"] is "X" and tue14["text"] is "X" and tue15["text"] is "X" and tue16["text"] is "X":
            tue08.configure(text="_", bg=default_color)
            tue09.configure(text="_", bg=default_color)
            tue10.configure(text="_", bg=default_color)
            tue11.configure(text="_", bg=default_color)
            tue13.configure(text="_", bg=default_color)
            tue14.configure(text="_", bg=default_color)
            tue15.configure(text="_", bg=default_color)
            tue16.configure(text="_", bg=default_color)
        else:
            tue08.configure(text="X", bg=default_color)
            tue09.configure(text="X", bg=default_color)
            tue10.configure(text="X", bg=default_color)
            tue11.configure(text="X", bg=default_color)
            tue13.configure(text="X", bg=default_color)
            tue14.configure(text="X", bg=default_color)
            tue15.configure(text="X", bg=default_color)
            tue16.configure(text="X", bg=default_color)

    elif str(day) == "3":
        if wed08["text"] is "X" and wed09["text"] is "X" and wed10["text"] is "X" and wed11["text"] is "X" and \
                wed13["text"] is "X" and wed14["text"] is "X" and wed15["text"] is "X" and wed16["text"] is "X":
            wed08.configure(text="_", bg=default_color)
            wed09.configure(text="_", bg=default_color)
            wed10.configure(text="_", bg=default_color)
            wed11.configure(text="_", bg=default_color)
            wed13.configure(text="_", bg=default_color)
            wed14.configure(text="_", bg=default_color)
            wed15.configure(text="_", bg=default_color)
            wed16.configure(text="_", bg=default_color)
        else:
            wed08.configure(text="X", bg=default_color)
            wed09.configure(text="X", bg=default_color)
            wed10.configure(text="X", bg=default_color)
            wed11.configure(text="X", bg=default_color)
            wed13.configure(text="X", bg=default_color)
            wed14.configure(text="X", bg=default_color)
            wed15.configure(text="X", bg=default_color)
            wed16.configure(text="X", bg=default_color)

    elif str(day) == "4":
        if thu08["text"] is "X" and thu09["text"] is "X" and thu10["text"] is "X" and thu11["text"] is "X" and \
                thu13["text"] is "X" and thu14["text"] is "X" and thu15["text"] is "X" and thu16["text"] is "X":
            thu08.configure(text="_", bg=default_color)
            thu09.configure(text="_", bg=default_color)
            thu10.configure(text="_", bg=default_color)
            thu11.configure(text="_", bg=default_color)
            thu13.configure(text="_", bg=default_color)
            thu14.configure(text="_", bg=default_color)
            thu15.configure(text="_", bg=default_color)
            thu16.configure(text="_", bg=default_color)
        else:
            thu08.configure(text="X", bg=default_color)
            thu09.configure(text="X", bg=default_color)
            thu10.configure(text="X", bg=default_color)
            thu11.configure(text="X", bg=default_color)
            thu13.configure(text="X", bg=default_color)
            thu14.configure(text="X", bg=default_color)
            thu15.configure(text="X", bg=default_color)
            thu16.configure(text="X", bg=default_color)

    elif str(day) == "5":
        if fri08["text"] is "X" and fri09["text"] is "X" and fri10["text"] is "X" and fri11["text"] is "X" and \
                fri13["text"] is "X" and fri14["text"] is "X" and fri15["text"] is "X" and fri16["text"] is "X":
            fri08.configure(text="_", bg=default_color)
            fri09.configure(text="_", bg=default_color)
            fri10.configure(text="_", bg=default_color)
            fri11.configure(text="_", bg=default_color)
            fri13.configure(text="_", bg=default_color)
            fri14.configure(text="_", bg=default_color)
            fri15.configure(text="_", bg=default_color)
            fri16.configure(text="_", bg=default_color)
        else:
            fri08.configure(text="X", bg=default_color)
            fri09.configure(text="X", bg=default_color)
            fri10.configure(text="X", bg=default_color)
            fri11.configure(text="X", bg=default_color)
            fri13.configure(text="X", bg=default_color)
            fri14.configure(text="X", bg=default_color)
            fri15.configure(text="X", bg=default_color)
            fri16.configure(text="X", bg=default_color)

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    # print(current_comb_num)
    # print("old", current_comb)
    # print("new", valid_combinations[current_comb_num - 1])

    # REUSED at filters
    if valid_combinations:
        try:
            if current_comb != valid_combinations[current_comb_num - 1]:
                # print("current is not new and might exist")
                for c in range(len(valid_combinations)):
                    if current_comb[0] is valid_combinations[c][0]:
                        current_comb_num = c + 1
                        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
                        # print("current is not new and exists")
                        break
                else:
                    # print("current is not new and no exist")
                    nav_info.set("1/" + str(len(valid_combinations)))
            else:
                # print("current is new")
                nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
        except IndexError:
            # print("current is not new and no exist error")
            current_comb_num = 1

        for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
            lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1], c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
    else:
        nav_info.set("0/0")

    # Display
    print("DAY {} STATUS CHANGE".format(day))
    display_combs()

    update_scheduler()


# Change Hour Status
def change_hour_status(h):
    """
    Make all the same hours available/ not available
    :param h:
    :return: None
    """
    global valid_combinations

    global current_comb
    global current_comb_num

    if str(h) == "08:40":
        if mon08["text"] is "X" and tue08["text"] is "X" and wed08["text"] is "X" and thu08["text"] is "X" and \
                fri08["text"] is "X":
            mon08.configure(text="_", bg=default_color)
            tue08.configure(text="_", bg=default_color)
            wed08.configure(text="_", bg=default_color)
            thu08.configure(text="_", bg=default_color)
            fri08.configure(text="_", bg=default_color)
        else:
            mon08.configure(text="X", bg=default_color)
            tue08.configure(text="X", bg=default_color)
            wed08.configure(text="X", bg=default_color)
            thu08.configure(text="X", bg=default_color)
            fri08.configure(text="X", bg=default_color)

    if str(h) == "09:40":
        if mon09["text"] is "X" and tue09["text"] is "X" and wed09["text"] is "X" and thu09["text"] is "X" and \
                fri09["text"] is "X":
            mon09.configure(text="_", bg=default_color)
            tue09.configure(text="_", bg=default_color)
            wed09.configure(text="_", bg=default_color)
            thu09.configure(text="_", bg=default_color)
            fri09.configure(text="_", bg=default_color)
        else:
            mon09.configure(text="X", bg=default_color)
            tue09.configure(text="X", bg=default_color)
            wed09.configure(text="X", bg=default_color)
            thu09.configure(text="X", bg=default_color)
            fri09.configure(text="X", bg=default_color)

    if str(h) == "10:40":
        if mon10["text"] is "X" and tue10["text"] is "X" and wed10["text"] is "X" and thu10["text"] is "X" and \
                fri10["text"] is "X":
            mon10.configure(text="_", bg=default_color)
            tue10.configure(text="_", bg=default_color)
            wed10.configure(text="_", bg=default_color)
            thu10.configure(text="_", bg=default_color)
            fri10.configure(text="_", bg=default_color)
        else:
            mon10.configure(text="X", bg=default_color)
            tue10.configure(text="X", bg=default_color)
            wed10.configure(text="X", bg=default_color)
            thu10.configure(text="X", bg=default_color)
            fri10.configure(text="X", bg=default_color)

    if str(h) == "11:40":
        if mon11["text"] is "X" and tue11["text"] is "X" and wed11["text"] is "X" and thu11["text"] is "X" and \
                fri11["text"] is "X":
            mon11.configure(text="_", bg=default_color)
            tue11.configure(text="_", bg=default_color)
            wed11.configure(text="_", bg=default_color)
            thu11.configure(text="_", bg=default_color)
            fri11.configure(text="_", bg=default_color)
        else:
            mon11.configure(text="X", bg=default_color)
            tue11.configure(text="X", bg=default_color)
            wed11.configure(text="X", bg=default_color)
            thu11.configure(text="X", bg=default_color)
            fri11.configure(text="X", bg=default_color)

    if str(h) == "13:40":
        if mon13["text"] is "X" and tue13["text"] is "X" and wed13["text"] is "X" and thu13["text"] is "X" and \
                fri13["text"] is "X":
            mon13.configure(text="_", bg=default_color)
            tue13.configure(text="_", bg=default_color)
            wed13.configure(text="_", bg=default_color)
            thu13.configure(text="_", bg=default_color)
            fri13.configure(text="_", bg=default_color)
        else:
            mon13.configure(text="X", bg=default_color)
            tue13.configure(text="X", bg=default_color)
            wed13.configure(text="X", bg=default_color)
            thu13.configure(text="X", bg=default_color)
            fri13.configure(text="X", bg=default_color)

    if str(h) == "14:40":
        if mon14["text"] is "X" and tue14["text"] is "X" and wed14["text"] is "X" and thu14["text"] is "X" and \
                fri14["text"] is "X":
            mon14.configure(text="_", bg=default_color)
            tue14.configure(text="_", bg=default_color)
            wed14.configure(text="_", bg=default_color)
            thu14.configure(text="_", bg=default_color)
            fri14.configure(text="_", bg=default_color)
        else:
            mon14.configure(text="X", bg=default_color)
            tue14.configure(text="X", bg=default_color)
            wed14.configure(text="X", bg=default_color)
            thu14.configure(text="X", bg=default_color)
            fri14.configure(text="X", bg=default_color)

    if str(h) == "15:40":
        if mon15["text"] is "X" and tue15["text"] is "X" and wed15["text"] is "X" and thu15["text"] is "X" and \
                fri15["text"] is "X":
            mon15.configure(text="_", bg=default_color)
            tue15.configure(text="_", bg=default_color)
            wed15.configure(text="_", bg=default_color)
            thu15.configure(text="_", bg=default_color)
            fri15.configure(text="_", bg=default_color)
        else:
            mon15.configure(text="X", bg=default_color)
            tue15.configure(text="X", bg=default_color)
            wed15.configure(text="X", bg=default_color)
            thu15.configure(text="X", bg=default_color)
            fri15.configure(text="X", bg=default_color)

    if str(h) == "16:40":
        if mon16["text"] is "X" and tue16["text"] is "X" and wed16["text"] is "X" and thu16["text"] is "X" and \
                fri16["text"] is "X":
            mon16.configure(text="_", bg=default_color)
            tue16.configure(text="_", bg=default_color)
            wed16.configure(text="_", bg=default_color)
            thu16.configure(text="_", bg=default_color)
            fri16.configure(text="_", bg=default_color)
        else:
            mon16.configure(text="X", bg=default_color)
            tue16.configure(text="X", bg=default_color)
            wed16.configure(text="X", bg=default_color)
            thu16.configure(text="X", bg=default_color)
            fri16.configure(text="X", bg=default_color)

    lecture_list = []
    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            button_text = str(child.cget("text"))
            course_id = str(button_text).split(" ")[0]
            def_course_code = str(button_text).split(" ")[1][:3]
            lecture_list.append([l for l in lecture_dict[course_id].keys() if course_id + " " + def_course_code in l])

    available_course(lecture_list)

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    # print(current_comb_num)
    # print("old", current_comb)
    # print("new", valid_combinations[current_comb_num - 1])

    # REUSED at filters
    if valid_combinations:
        try:
            if current_comb != valid_combinations[current_comb_num - 1]:
                # print("current is not new and might exist")
                for c in range(len(valid_combinations)):
                    if current_comb[0] is valid_combinations[c][0]:
                        current_comb_num = c + 1
                        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
                        # print("current is not new and exists")
                        break
                else:
                    # print("current is not new and no exist")
                    nav_info.set("1/" + str(len(valid_combinations)))
            else:
                # print("current is new")
                nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
        except IndexError:
            # print("current is not new and no exist error")
            current_comb_num = 1

        for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
            lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1], c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
    else:
        nav_info.set("0/0")

    # Display
    print("HOUR {} STATUS CHANGE".format(h))
    display_combs()

    update_scheduler()


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
        tk.Button(frame_course_code, text=course, padx=20, pady=10, command=lambda c=course: add_lec_ids(c))\
            .place(relwidth=0.1, relheight=0.1, relx=relx_counter, rely=rely_counter)

        course_col += 1
        relx_counter += 0.1

        if course_col == max_course_col:
            rely_counter += 0.1
            relx_counter = 0.05
            course_col = 0


# Scheduler Frame Day Buttons
def create_day_buttons():
    """
    Create Scheduler Frame 'day' buttons
    :return: None
    """
    day_relx_counter = 0.05
    day_rely_counter = 0.05
    day_list = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    # day_list = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in range(6):
        if day_list[day] == "":
            day_btn = tk.Button(frame_scheduler, text=day_list[day], padx=20, pady=10, relief=tk.GROOVE,
                                activeforeground="red")

            day_btn.place(relwidth=0.15, relheight=0.1, relx=day_relx_counter, rely=day_rely_counter)
        else:
            day_btn = tk.Button(frame_scheduler, text=day_list[day], padx=20, pady=10, relief=tk.GROOVE,
                                activeforeground="red", command=lambda d=day: change_day_status(d))

            day_btn.place(relwidth=0.15, relheight=0.1, relx=day_relx_counter, rely=day_rely_counter)

        day_relx_counter += 0.15


# Scheduler Frame Hour Buttons
def create_hour_buttons():
    """
    Create Scheduler Frame 'hour' buttons
    :return: None
    """
    hour_relx_counter = 0.05
    hour_rely_counter = 0.15
    hour_list = ["08:40", "09:40", "10:40", "11:40", "12:40", "13:40", "14:40", "15:40", "16:40"]
    for h in range(9):
        if hour_list[h] == "12:40":
            hour_btn = tk.Button(frame_scheduler, text=hour_list[h], padx=20, pady=10, relief=tk.GROOVE,
                                 activeforeground="red")

            hour_btn.place(relwidth=0.15, relheight=0.09, relx=hour_relx_counter, rely=hour_rely_counter)

        else:
            hour_btn = tk.Button(frame_scheduler, text=hour_list[h], padx=20, pady=10, relief=tk.GROOVE,
                                 activeforeground="red", command=lambda x=hour_list[h]: change_hour_status(x))

            hour_btn.place(relwidth=0.15, relheight=0.09, relx=hour_relx_counter, rely=hour_rely_counter)

        hour_rely_counter += 0.09


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
                tk.Button(frame_section_filter, bg="green", text=s, command=lambda l_id=s: disable_section(l_id))\
                    .pack(fill=tk.X)
            elif s in section_blacklist:
                tk.Button(frame_section_filter, bg="red", text=s, command=lambda l_id=s: enable_section(l_id))\
                    .pack(fill=tk.X)
            else:
                tk.Button(frame_section_filter, bg="yellow", text=s, state=tk.DISABLED).pack(fill=tk.X)
            no_lecture = False

        tk.Label(frame_section_filter, text="_______________________________________________________").pack(fill=tk.X)

    if no_lecture:
        tk.Label(frame_section_filter, text="No Lectures to Filter!", fg="red").pack(fill=tk.X)
        tk.Label(frame_section_filter, text="_______________________________________________________").pack(fill=tk.X)

    section_canvas.create_window(0, 0, anchor='nw', window=frame_section_filter)
    section_canvas.update_idletasks()

    section_canvas.configure(scrollregion=section_canvas.bbox('all'), yscrollcommand=section_scroll_y.set)

    section_canvas.place(relwidth=0.95, relheight=1, relx=0, rely=0)
    section_scroll_y.place(relwidth=0.05, relheight=1, relx=0.95, rely=0)

    section_canvas.bind_all("<MouseWheel>", section_on_mousewheel)

    section_filter.bind('f', lambda e: section_filter.destroy())
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
            child.configure(bg="red", command=lambda l_id=sec: enable_section(sec))


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
            child.configure(bg="green", command=lambda l_id=sec: disable_section(sec))


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
    # print(section_blacklist)
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

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    if valid_combinations:
        try:
            if current_comb != valid_combinations[current_comb_num - 1]:
                # print("current is not new and might exist")
                for c in range(len(valid_combinations)):
                    if current_comb[0] is valid_combinations[c][0]:
                        current_comb_num = c + 1
                        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
                        # print("current is not new and exists")
                        break
                else:
                    # print("current is not new and no exist")
                    nav_info.set("1/" + str(len(valid_combinations)))
            else:
                # print("current is new")
                nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
        except IndexError:
            # print("current is not new and no exist error")
            current_comb_num = 1

        for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
            lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1], c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
    else:
        nav_info.set("0/0")

    print("SECTION FILTER\nBlacklisted Sections {}\n".format(section_blacklist))
    display_combs()

    update_scheduler()


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

        # print(lecture_id)
        # print(teacher_list)
        # print(valid_teachers)

        tk.Label(frame_teacher_filter, text=def_lecture_id, anchor=tk.W).pack(fill=tk.X)

        for t in teacher_list:
            if t in valid_teachers:
                tk.Button(frame_teacher_filter, bg="green", text=t, command=lambda l_id=t: disable_teacher(l_id))\
                    .pack(fill=tk.X)
            elif t in teacher_blacklist:
                tk.Button(frame_teacher_filter, bg="red", text=t, command=lambda l_id=t: enable_teacher(l_id))\
                    .pack(fill=tk.X)
            else:
                tk.Button(frame_teacher_filter, bg="yellow", text=t, state=tk.DISABLED).pack(fill=tk.X)
            no_lecture = False

        tk.Label(frame_teacher_filter, text="_______________________________________________________").pack(fill=tk.X)

    if no_lecture:
        tk.Label(frame_teacher_filter, text="No Lectures to Filter!", fg="red").pack(fill=tk.X)
        tk.Label(frame_teacher_filter, text="_______________________________________________________").pack(fill=tk.X)

    teacher_canvas.create_window(0, 0, anchor='nw', window=frame_teacher_filter)
    teacher_canvas.update_idletasks()

    teacher_canvas.configure(scrollregion=teacher_canvas.bbox('all'), yscrollcommand=teacher_scroll_y.set)

    teacher_canvas.place(relwidth=0.95, relheight=1, relx=0, rely=0)
    teacher_scroll_y.place(relwidth=0.05, relheight=1, relx=0.95, rely=0)

    teacher_canvas.bind_all("<MouseWheel>", teacher_on_mousewheel)

    teacher_filter.bind('f', lambda e: teacher_filter.destroy())
    teacher_filter.protocol("WM_DELETE_WINDOW", close_teacher_filter)
    teacher_filter.mainloop()


# Disable Section
def disable_teacher(teach):
    """
    Make green(available) teachers red(unavailable)
    :param teach:
    :return: None
    """
    # print("disable", teach)
    for child in frame_teacher_filter.winfo_children():
        if child.winfo_class() == "Button" and str(child.cget("text")) == str(teach):
            child.configure(bg="red", command=lambda l_id=teach: enable_teacher(teach))


# Enable Section
def enable_teacher(teach):
    """
    Make red(unavailable) teachers green(available)
    :param teach:
    :return: None
    """
    # print("enable ", teach)
    for child in frame_teacher_filter.winfo_children():
        if child.winfo_class() == "Button" and str(child.cget("text")) == str(teach):
            child.configure(bg="green", command=lambda l_id=teach: disable_teacher(teach))


# Close Section Filter
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
    # print(teacher_blacklist)
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

    for child in frame_lecture_info.winfo_children():
        if child.winfo_class() == "Button":
            child.destroy()

    if valid_combinations:
        try:
            if current_comb != valid_combinations[current_comb_num - 1]:
                # print("current is not new and might exist")
                for c in range(len(valid_combinations)):
                    if current_comb[0] is valid_combinations[c][0]:
                        current_comb_num = c + 1
                        nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
                        # print("current is not new and exists")
                        break
                else:
                    # print("current is not new and no exist")
                    nav_info.set("1/" + str(len(valid_combinations)))
            else:
                # print("current is new")
                nav_info.set(str(current_comb_num) + "/" + str(len(valid_combinations)))
        except IndexError:
            # print("current is not new and no exist error")
            current_comb_num = 1

        for l in reversed(list(valid_combinations[current_comb_num - 1])):
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
            lecture_info = "{} {}-{} {} ".format(c_code.split(" ")[0], c_code.split(" ")[1], c_section, course_teacher)
            # print("{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1], c_section, course_teacher))
            tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                      command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)
    else:
        nav_info.set("0/0")

    print("TEACHER FILTER\nBlacklisted Teachers {}\n".format(teacher_blacklist))
    display_combs()

    update_scheduler()


# Teacher Filter Mouse Wheel Bind
def teacher_on_mousewheel(event):
    """
    Bind the scrolling event of teacher_canvas to teacher_filter_scroll
    :param event:
    :return: None
    """
    teacher_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# Clear All Filters
def clear_filters_ask():
    """
    Ask the user, then clear all filters
    :return: None
    """
    global teacher_blacklist
    global section_blacklist
    global current_comb_num

    if messagebox.askokcancel("Clear Filters", "Do you want to clear the filters?"):
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

        for child in frame_lecture_info.winfo_children():
            child.destroy()

        clear_scheduler()

        if valid_combinations:
            if valid_combinations[current_comb_num - 1]:
                for l in reversed(list(valid_combinations[current_comb_num - 1])):
                    # print(l)
                    c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

                    course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                    # Frame Lecture Info
                    lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                         c_section, course_teacher)
                    tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                              command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

            nav_info.set("1/" + str(len(valid_combinations)))
            current_comb_num = 1
        else:
            nav_info.set("0/0")

        print("CLEAR FILTERS\n")
        display_combs()

        update_scheduler()


# Clear All Filters Ask
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

    for child in frame_lecture_info.winfo_children():
        child.destroy()

    clear_scheduler()

    if valid_combinations:
        if valid_combinations[current_comb_num - 1]:
            for l in reversed(list(valid_combinations[current_comb_num - 1])):
                # print(l)
                c_name, c_section = str(l).split("-")[0], str(l).split("-")[1]

                course_teacher = lecture_dict[c_name.split(" ")[0]][str(c_name) + "-" + str(c_section)][0]

                # Frame Lecture Info
                lecture_info = "{} {}-{} {} ".format(c_name.split(" ")[0], c_name.split(" ")[1],
                                                     c_section, course_teacher)
                tk.Button(frame_lecture_info, text=lecture_info, fg="red", anchor=tk.W,
                          command=lambda l_info=lecture_info: delete_button(l_info)).pack(side=tk.TOP, fill=tk.X)

        nav_info.set("1/" + str(len(valid_combinations)))
        current_comb_num = 1
    else:
        nav_info.set("0/0")

    update_scheduler()


# Close Main Window
def close_main():
    """
    Before the main window is closed, ask the user to confirm the exit
    :return: None
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()


# Combinations
all_combinations, valid_combinations, current_comb = [], [], []
current_comb_num = 0

# Blacklists
section_blacklist, teacher_blacklist = [], []

# Undo / Redo
undo_redo_list, undo_redo_counter = [], -1

# Startup Functions

update_scheduler()

create_course_code_buttons()

create_day_buttons()

create_hour_buttons()


# Options Frame Buttons
s_filter = tk.Button(frame_options, text="Section Filter", relief=tk.GROOVE, command=filter_section)
s_filter.place(relwidth=1, relheight=0.25, relx=0, rely=0)

t_filter = tk.Button(frame_options, text="Teacher Filter", relief=tk.GROOVE, command=filter_teacher)
t_filter.place(relwidth=1, relheight=0.25, relx=0, rely=0.25)

btn_clear_filter = tk.Button(frame_options, text="Clear Filters", relief=tk.GROOVE, command=clear_filters_ask)
btn_clear_filter.place(relwidth=1, relheight=0.25, relx=0, rely=0.50)

# Clear
clear = tk.Button(frame_options, text="Clear", relief=tk.GROOVE, command=clear_all_ask)
clear.place(relwidth=1, relheight=0.25, relx=0, rely=0.75)


# Main Window Settings
root.bind('a', lambda e: screenshot())
root.bind('s', lambda e: save_program())
root.bind('d', lambda e: load_program())
root.bind('f', lambda e: root.destroy())

root.bind('z', lambda e: fullscreen())
root.bind('x', lambda e: no_fullscreen())
root.bind('c', lambda e: clear_all_ask())

root.bind('<Left>', lambda e: back(2))
root.bind('<Right>', lambda e: forward(2))

root.bind('<Escape>', lambda e: no_fullscreen())

root.protocol("WM_DELETE_WINDOW", close_main)
root.mainloop()
