# SugarScope AI - Machine Learning Project
![](resources/read_me_preview.PNG?raw=true)

## Background
SugarScope AI is a Machine Learning application that allows you to get real time image classification predictions! This application uses Microsoft's Lobe backend to make inferences from an onnx model.

## Features
- Real time image classification predictions from RTSP Streaming camera input
- GUI built with Tkinter library
- Uses treading library to handle grabbing camera frames


![](resources/sugarscope_gif.gif?raw=true)

## How to use
- Install all necessary libraries and dependencies.
- Update the RTSP streaming link and model path in the config.xml file.
- Run the main.py file with python main.py.
    
Begin using the GUI to get live predictions from your RTSP Stream!

## Optimizations
- Use multithreading to improve performance when grabbing camera frames
- Implement model optimization techniques to optimize for accuracy instead of speed
- Change the frame rate to one that the network can handle

## Lessons Learned
- RTSP Streaming can be challenging to work with
- Tkinter is a simple and easy to use GUI library
- Microsoft Lobe is a powerful and easy to use tool for making inferences from an onnx model
