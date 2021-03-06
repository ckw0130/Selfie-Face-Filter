import cv2 as cv
import torch
import models

def main():
    face_classifier = cv.CascadeClassifier('../data/haarcascade_frontalface_default.xml')
    capture = cv.VideoCapture(0)

    pretrained = torch.load("saved_model/2018-12-10_12:26:18.pt")
    conv_net = models.ConvNet()
    conv_net.load_state_dict(pretrained['model_state_dict'])

    while True:
        ret, frame = capture.read()
        if not ret:
           continue

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv.CASCADE_SCALE_IMAGE)

        for (x, y, w, h) in faces:
            start_y = y-int(h*0.25)
            if start_y < 0:
                continue

            frame = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)

            # cv.rectangle(frame, (x, start_y), (x+w, y+h), (0, 255, 0), 2)

            face = frame[start_y:y+h, x:x+w]
            face = cv.cvtColor(face, cv.COLOR_BGR2GRAY)
            face = cv.resize(face, (48, 48)).reshape((1, 1, 48, 48))

            input = torch.FloatTensor(face)
            output = conv_net(input)
            _, predicted = torch.max(output.data, 1)

            if predicted.data[0] == 0:
                s_img = cv.imread("../assets/thug_life.png", -1)
                print("Angry")
            elif predicted.data[0] == 1:
                s_img = cv.imread("../assets/shiba.png", -1)
                print("Happy")
            elif predicted.data[0] == 2:
                s_img = cv.imread("../assets/kitten.png", -1)
                print("Neutral")

            resizedFilter = cv.resize(s_img, (w, h), fx=0.5, fy=0.5)
            w1, h1, _ = resizedFilter.shape

            for i in range(0,w1):
                for j in range(0,h1):
                    if resizedFilter[i,j][3] != 0:
                        if predicted.data[0] == 0:
                            frame[y+i, x+j] = resizedFilter[i, j]
                        else:
                            frame[start_y+i, x+j] = resizedFilter[i, j]

        cv.imshow('Video', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()