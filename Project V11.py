import cv2
import math
import numpy as np

const_VIDEO_DELAY = 1

def count_frames(video, override=False):
    total = 0

    if override:
        total = count_frames_manual(video)

    else:
        try:
            if is_cv3():
                total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            else:
                total = int(video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

        except:
            total = count_frames_manual(video)

    video.release()

    return total


def count_frames_manual(video):
    total = 0

    while True:
        (grabbed, frame) = video.read()

        if not grabbed:
            break

        total += 1

    return total    


def resize_image(image, appropriate_height, appropriate_width):
    image_height, image_width = image.shape[:2]

    scaling_factor = appropriate_height / float(image_height)
    if appropriate_width /float(image_width) < scaling_factor:
        scaling_factor = float(image_width) / appropriate_width

    if scaling_factor > 1:
        scaled_image = cv2.resize(image, None, fx = scaling_factor, fy = scaling_factor, interpolation = cv2.INTER_AREA)

    elif scaling_factor < 1:
        scaled_image = cv2.resize(image, None, fx = scaling_factor, fy = scaling_factor, interpolation = cv2.INTER_CUBIC)
        
    return scaled_image

def print_timeline(starting_string, seconds, file_name = None):
    second = int(seconds / 1000);
    minute = 0
    hour = 0

    if second >= 60:
        minute = int(second / 60)
        second %= 60

        if minute >= 60:
            hour = int(minute / 60)
            minute %= 60
            
    print(starting_string, hour, ':', minute, ':', second, '.', file = file_name)
    return


def video_in_video_searching():

    with open('File Information.txt') as file_information:
        reference_video_name = file_information.readline()
        template_video_name = file_information.readline()
        threshold = float(file_information.readline())


    saved_threshold = threshold

    reference_video_name = reference_video_name.strip()
    template_video_name = template_video_name.strip()


    frame_count_of_reference_video = count_frames(cv2.VideoCapture(reference_video_name))
    frame_count_of_template_video = count_frames(cv2.VideoCapture(template_video_name))

    reference_video = cv2.VideoCapture(reference_video_name)
    template_video = cv2.VideoCapture(template_video_name)

    return_value_of_template_video, first_frame_of_template_video = template_video.read()
    gray_frame_of_first_frame_of_template_video = cv2.cvtColor(first_frame_of_template_video, cv2.COLOR_BGR2GRAY)

    current_count_of_reference_video = 0
    current_count_of_template_video = 1

    matched_count = 0

    

    while current_count_of_reference_video < frame_count_of_reference_video:
        return_value_of_reference_video, frame_of_reference_video = reference_video.read()

        if return_value_of_reference_video == False:
            break

        gray_frame_of_reference_video = cv2.cvtColor(frame_of_reference_video, cv2.COLOR_BGR2GRAY)
        cv2.imshow('Reference video', resize_image(gray_frame_of_reference_video, 768, 1366))
        print_timeline('Reference video is at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))
        cv2.waitKey(const_VIDEO_DELAY)

        height_of_gray_frame_of_reference_video, width_of_gray_frame_of_reference_video = gray_frame_of_reference_video.shape[:2]
        height_of_gray_frame_of_first_frame_of_template_video, width_of_gray_frame_of_first_frame_of_template_video = gray_frame_of_first_frame_of_template_video.shape[:2]
        
        if height_of_gray_frame_of_reference_video != height_of_gray_frame_of_first_frame_of_template_video or width_of_gray_frame_of_reference_video != width_of_gray_frame_of_first_frame_of_template_video:
            gray_frame_of_first_frame_of_template_video = resize_image(gray_frame_of_first_frame_of_template_video, height_of_gray_frame_of_reference_video, width_of_gray_frame_of_reference_video)
        
        matching_result = cv2.matchTemplate(gray_frame_of_reference_video, gray_frame_of_first_frame_of_template_video, cv2.TM_CCOEFF_NORMED)

        minimum_value, maximum_value, minimum_location, maximum_location = cv2.minMaxLoc(matching_result)

        matching_result = maximum_value

        print('Matching result is:', matching_result, '\n\n');

        if matching_result >= threshold:
            
            previous_threshold = threshold

            #Getting the maximum matched frame

            condition = True

            while condition:
                return_value_of_reference_video, frame_of_reference_video = reference_video.read()

                if return_value_of_reference_video == False:
                    break

                gray_frame_of_reference_video = cv2.cvtColor(frame_of_reference_video, cv2.COLOR_BGR2GRAY)
                cv2.imshow('Reference video', resize_image(gray_frame_of_reference_video, 768, 1366))
                print_timeline('Reference video is at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))
                cv2.waitKey(const_VIDEO_DELAY)

                height_of_gray_frame_of_reference_video, width_of_gray_frame_of_reference_video = gray_frame_of_reference_video.shape[:2]
                
                matching_result = cv2.matchTemplate(gray_frame_of_reference_video, gray_frame_of_first_frame_of_template_video, cv2.TM_CCOEFF_NORMED)

                minimum_value, maximum_value, minimum_location, maximum_location = cv2.minMaxLoc(matching_result)

                matching_result = maximum_value

                print('Matching result is:', matching_result);
                print('Threshold is:', threshold, '\n\n');

                previous_threshold = threshold
                threshold = matching_result

                condition = (previous_threshold <= threshold)

            
            if matched_count == 0:
                output_information = open('Output Information.txt', 'w')
            else:
                output_information = open('Output Information.txt', 'a')
                
            print_timeline('Matching started at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC), output_information)
            print_timeline('Matching started at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))
            print('Matching result is:', previous_threshold, '\n\n', file = output_information)

            matched_count += 1

            first_time = 1
            
            cv2.imshow('Template video', resize_image(gray_frame_of_first_frame_of_template_video, 1366, 768))
            cv2.waitKey(const_VIDEO_DELAY)

            print_timeline('Reference video is at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))
            print_timeline('Template video is at: ', template_video.get(cv2.CAP_PROP_POS_MSEC))

            print('\n\n')
            
            while current_count_of_template_video < frame_count_of_template_video:

                #Skipping 1 second amount of frames from reference video
                
                for x in range(1, int(reference_video.get(cv2.CAP_PROP_FPS)) - 1 - first_time):
                    return_value_of_reference_video, frame_of_reference_video = reference_video.read()
                    gray_frame_of_reference_video = cv2.cvtColor(frame_of_reference_video, cv2.COLOR_BGR2GRAY)
                    cv2.imshow('Reference video', resize_image(gray_frame_of_reference_video, 1366,768))
                    cv2.waitKey(const_VIDEO_DELAY)
                    print_timeline('Reference video is at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))
                    current_count_of_reference_video += 1
                    if current_count_of_reference_video >= frame_count_of_reference_video:
                        break
                    
                if first_time != 0:
                    first_time = 0
                
                if current_count_of_reference_video >= frame_count_of_reference_video:
                    break

                #Taking another frame from reference
                
                return_value_of_reference_video, frame_of_reference_video = reference_video.read()
                gray_frame_of_reference_video = cv2.cvtColor(frame_of_reference_video, cv2.COLOR_BGR2GRAY)
                cv2.imshow('Reference video', resize_image(gray_frame_of_reference_video, 1366,768))
                cv2.waitKey(const_VIDEO_DELAY)
                print_timeline('Reference video is at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))
                current_count_of_reference_video += 1

                #Skipping 1 second amount of frames from template video

                for x in range(1, int(template_video.get(cv2.CAP_PROP_FPS)) - 1):
                    return_value_of_template_video, frame_of_template_video = template_video.read()
                    gray_frame_of_template_video = cv2.cvtColor(frame_of_template_video, cv2.COLOR_BGR2GRAY)
                    cv2.imshow('Template video', resize_image(gray_frame_of_template_video, 1366, 768))
                    cv2.waitKey(const_VIDEO_DELAY)
                    print_timeline('Template video is at: ', template_video.get(cv2.CAP_PROP_POS_MSEC))
                    current_count_of_template_video += 1
                    if current_count_of_template_video >= frame_count_of_template_video:
                        break
                    

                if current_count_of_template_video >= frame_count_of_template_video:
                    break

                #Taking another frame from template
                
                return_value_of_template_video, frame_of_template_video = template_video.read()
                gray_frame_of_template_video = cv2.cvtColor(frame_of_template_video, cv2.COLOR_BGR2GRAY)
                cv2.imshow('Template video', resize_image(gray_frame_of_template_video, 1366, 768))
                cv2.waitKey(const_VIDEO_DELAY)
                print_timeline('Template video is at: ', template_video.get(cv2.CAP_PROP_POS_MSEC))
                current_count_of_template_video += 1

                height_of_gray_frame_of_reference_video, width_of_gray_frame_of_reference_video = gray_frame_of_reference_video.shape[:2]
                height_of_gray_frame_of_template_video, width_of_gray_frame_of_template_video = gray_frame_of_template_video.shape[:2]
        
                if height_of_gray_frame_of_reference_video != height_of_gray_frame_of_template_video or width_of_gray_frame_of_reference_video != width_of_gray_frame_of_template_video:
                    gray_frame_of_template_video = resize_image(gray_frame_of_template_video, height_of_gray_frame_of_reference_video, width_of_gray_frame_of_reference_video)


                matching_result = cv2.matchTemplate(gray_frame_of_reference_video, gray_frame_of_template_video, cv2.TM_CCOEFF_NORMED)

                minimum_value, maximum_value, minimum_location, maximum_location = cv2.minMaxLoc(matching_result)

                matching_result = maximum_value

                print('Matching result inside matched part of reference video is:', matching_result, file = output_information);
                print('Matching result inside matched part of reference video is:', matching_result);

                if matching_result >= threshold:
                    print('Matching continued.\n\n', file = output_information)
                    print('Matching continued.\n\n')

                else:
                    print('Matching abruptly stopped.\n\n', file = output_information)
                    print('Matching abruptly stopped.\n\n')
                    cv2.destroyWindow('Template video')
                    break
                
            cv2.destroyWindow('Template video')

            #ending matching part
            
            print_timeline('Matching ended at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC), output_information)
            print_timeline('Matching ended at: ', reference_video.get(cv2.CAP_PROP_POS_MSEC))

            output_information.close()
            
            template_video = cv2.VideoCapture(template_video_name)

            return_value_of_template_video, first_frame_of_template_video = template_video.read()
            gray_frame_of_first_frame_of_template_video = cv2.cvtColor(first_frame_of_template_video, cv2.COLOR_BGR2GRAY)
            current_count_of_template_video = 1

            threshold = saved_threshold
        
        else:
            current_count_of_reference_video += 1

    template_video.release()
    reference_video.release()
    cv2.destroyAllWindows()

    return




print('Program started.')


video_in_video_searching()


print('Program ended.')
