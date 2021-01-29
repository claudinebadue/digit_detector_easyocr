import argparse
import cv2
import matplotlib.pyplot as plt
import PIL
from PIL import ImageDraw
import easyocr
import itertools
import operator


DEBUG_FLAG = False

WINDOW_SIZE = 11

CONFIDENCE_THRESHOLD = 0.1


colors = ["red", "green", "blue", "violet", "grey", "white"]

# The first pair of numbers is the range of the y-axis in the original image, while the second is the range of the x-axis
crops = [[0, 0, 0, 0],
         [300, 550, 1100, 1450], # Camera 1
         [50, 700, 750, 1400], # Camera 2
         [200, 900, 550, 1200], # Camera 3
         [50, 950, 350, 1250], # Camera 4
         [100, 600, 600, 1300], # Camera 5
         [0, 0, 0, 0]]

argparser = argparse.ArgumentParser(
    description='Digit Detector Based on EasyOCR')

argparser.add_argument(
    '-g',
    '--ground_truth',
    default="ground_truth.txt",
    help='ground truth text file')

argparser.add_argument(
    '-n',
    '--train_numbers',
    default="train_numbers.txt",
    help='train numbers text file')


def parse_arguments():
    args = argparser.parse_args()
    print("ground truth text file = ", args.ground_truth)
    print("train numbers text file = ", args.train_numbers)
    
    ground_truth_file_name = args.ground_truth
    ground_truth = open(ground_truth_file_name, 'r') 
    ground_truth_lines = ground_truth.readlines() 
    
    num_lines = 0
    ground_truth = []
    for ground_truth_line in ground_truth_lines:
        if ground_truth_line[0] == '#':
            continue
        # Strips the newline character 
        gt_line_split = ground_truth_line.split()
        ground_truth.append(gt_line_split)
        num_lines = num_lines + 1

    train_numbers_file_name = args.train_numbers
    train_numbers = open(train_numbers_file_name, 'r') 
    train_numbers_lines = train_numbers.readlines() 
    
    train_numbers = []
    for train_numbers_line in train_numbers_lines:
        if train_numbers_line[0] == '#':
            continue
        tn_line_split = train_numbers_line.split()
        train_numbers.append(tn_line_split)  
        
    return args, ground_truth, train_numbers


def draw_boxes(image, bounds, color='yellow', width=2):
    draw = ImageDraw.Draw(image)
    i = 0
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=colors[i], width=width)
        i = i + 1
        if i >= len(colors):
            i = 0

    return image


def get_train_number_easyocr_old(detections):
    i = 0
    max_confidence = 0.0
    selected_color = 0
    best_number = ''
    color = 0
    for detection in detections:
        confidence = detection[2]
        print(detection[1], confidence, colors[color])
        if confidence < CONFIDENCE_THRESHOLD or detection[1] == 'VALE' or detection[1] == '':
            color = color + 1
            continue
        
        if True:# i == 0 or i == 1:
            if confidence > max_confidence:
                max_confidence = confidence
                best_number = detection[1]
                selected_color = color
        i = i + 1
        color = color + 1
        if color >= len(colors):
            color = 0

    print("selected_color: ", colors[selected_color])
    train_number = 0
    for c in best_number:
        if c.isdigit():
            train_number = 10 * train_number + int(c)
        else:
            if c == 'l' or c == '|' or c == 'I' or c == '(' or c == '!':
                train_number = 10 * train_number + 1
            elif c == 'G' or c == 'g':
                train_number = 10 * train_number + 6
            elif c == 'S' or c == 's':
                train_number = 10 * train_number + 5

    return train_number


def train_number_exists(train_number, train_numbers):
    exists = False
    for tn_line in train_numbers:
        if tn_line[0] != "ATIVO" and int(tn_line[0]) == train_number:
            exists = True

    #print("exists =", exists)

    return(exists)

    
def adjust_detected_train_number(detection, train_numbers):
    confidence = detection[2]
    train_number = 0
    for c in detection[1]:
        if c.isdigit():
            train_number = 10 * train_number + int(c)
        else:
            if c == 'I' or c == 'i' or c == 'L' or c == 'l' or c == 'T' or c == 't' or c == '!' or c == '(' or c == ')' or c == '|' or  c == '[' or c == ']' or c == '/':
                train_number = 10 * train_number + 1
            elif c == 'G':
                train_number = 10 * train_number + 6
            elif c == 'S' or c == 's':
                train_number = 10 * train_number + 5
            #elif c == 'B':
            #    train_number = 10 * train_number + 8

    #print("train_number = ", train_number) 
    #print("confidence = ", confidence)                 

    #if confidence < CONFIDENCE_THRESHOLD or train_number < 100 or train_number > 9999: 
    if confidence < CONFIDENCE_THRESHOLD or train_number_exists(train_number, train_numbers) == False: 
        confidence = 0.0
    
    return(detection[0], train_number, confidence)

def get_train_number_easyocr(detections, train_numbers):  
    i = 0
    max_confidence = 0.0
    selected_color = 0
    best_number = 0
    color = 0
    for detection_ in detections:
        detection = adjust_detected_train_number(detection_, train_numbers)
        train_number = detection[1]        
        confidence = detection[2]
    
        print(colors[color], train_number, confidence)
        
        if confidence > max_confidence:
            max_confidence = confidence
            best_number = train_number
            selected_color = color
        i = i + 1
        color = color + 1
        if color >= len(colors):
            color = 0

    print("selected_color = ", colors[selected_color])
     
    return best_number

# https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
def most_common(L):
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item

    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        
        #print(item, count);
        print("most_common_number = ", item)
        print("frequency = ", count)
        
        return count, -min_index
    
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def check_last_detections(last_detections):
    t = last_detections[-1]
    last_detections_0 = [x[0] for x in last_detections]
    t_most_common = most_common(last_detections_0)
    
    return(t_most_common == t[1])

# main
if __name__ == '__main__':
    args, ground_truth, train_numbers = parse_arguments()
    
    # Carrega o ORC
    reader = easyocr.Reader(['pt','en'])

    last_detections = []    
    counter = 0
    num_images_examined = 0
    hits = 0    
    for gt_line in ground_truth:
        image = cv2.imread(gt_line[0])
        image = image[:,:,::-1]
        
        camera_id = int(gt_line[2])
        image = image[crops[camera_id][0]:crops[camera_id][1], crops[camera_id][2]:crops[camera_id][3]]

        cv2.imwrite("caco.jpg", image)
        detections = reader.readtext("caco.jpg") 
        
        print("****")
        print(detections)
    
       # Computa a taxa de acertos
        train_number_detected = get_train_number_easyocr(detections, train_numbers)
        gt_train_number = int(gt_line[1])
        t = (train_number_detected, gt_train_number)
        last_detections.append(t)
        num_images_examined = num_images_examined + 1
        counter = counter + 1
        if check_last_detections(last_detections):
            hits = hits + 1
            print(gt_line[0], ": Acertou! ", train_number_detected, " = ", gt_train_number, ", num_images_examined = ", num_images_examined, ", % correct = ", hits / num_images_examined)
        else:
            print(gt_line[0], ": Errou... ", train_number_detected, " != ", gt_train_number, ", num_images_examined = ", num_images_examined, ", % correct = ", hits / num_images_examined)
        
        last_detections.pop(0)
         
        if DEBUG_FLAG:
            im = PIL.Image.open("caco.jpg")
            image = draw_boxes(im, detections)
            plt.imshow(image)    
            plt.show()
            #plt.show(block=False)
            #plt.pause(0.1)
        

