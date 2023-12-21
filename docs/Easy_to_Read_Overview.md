
# An Easy-to-Read Overview of the Robot Car Project

Welcome!! Bienvenue!! Tunngasugit!!

(I am in Canada -- these are our official languages -- English, French and a semi-official third (indigenous) language of Inuktitut.)

If you are interested in starting this project, you should read this file first. 

Why? Because it is written from from a first-person viewpoint that tries to answer the big questions of why do this project, how to start, how to implement, and so on. If you think back to learning a new subject in university -- wasn't it better to get tutorial help from a friend who just learned it rather than someone who had already knew the subject for twenty years?  That's because the new learner has in his/her brain the steps that need to be overcome, while the experienced person has integrated these steps and may not teach them.
I am that new learner -- trying to figure out how to even start this project. Let me guide you into what I believe you will find will be a very advantageous and satisfying project.


**Busy Life Note**

I am super busy until the middle of February 2024 -- thus I will update this project readme/wiki slowly until then. By mid February I will start writing much more often.
Any questions before? Please email me to:  hschneidermd@alum.mit.edu

--

![assembled robot car](robotcar.jpg)


**Why Build a Robot Car?**

Embodiment is crucial to the emergence of real AGI, as well as understanding the operation of the mammalian brain.
For a good overview of the importance of grounding your AI/AGI please consider my paper:
[cca5 inductive analogical soln to grounding problem](https://www.sciencedirect.com/science/article/abs/pii/S1389041722000493?via%3Dihub) [archive preprint](https://github.com/howard8888/insomnia/blob/master/analogical%20inductive%20preprint.pdf)

Even if Tesla Bots, for sake of example, were available, you wouldn't want to use such a complex system for the prototype stages of your AI/AGI project or theoretical project. You want a capable but simple enough robotic system that you have direct access to via Python, which is what this robotic car project allows. You will now have an embodiment to use with your AI/AGI. Even if you work mainly theoretically, the robotic car project can be very useful in terms of demonstrations and proof of concept.

![tesla bot gen 2](teslabot.jpg)



**Step #1 -- Decide if you want to do the Project**

Your first step should be to decide to build this robotic car project. Are you working on an AI/AGI project that it could be useful for? (Actually, it is probably useful for most projects, including LLMs.) Do you have an interest in robotics and would like to see an interface to an AI project?

In terms of monetary cost expect to spend about US$200 on the project (I know the Amazon.com prices are not this high, but shipping to other countries, extra parts from AliExpress, etc will push up the price). 

In terms of electronics expertise, very little is needed if everything gets assembled correctly and all parts are working. If you want to modify the design, if there is more advanced troubleshooting, then of course more is better.
In terms of software expertise, you need to be comfortable moving around files and using Python. The Arduino IDE and code you can install and copy without great expertise. Of course, if you have the time, you can spend more hours getting more expertise in the Arduino ecosystem and more familiarity with the systems Python routines used by the project.



**Step #2 -- Purchase the Robot Car kit**

I assume you already have a Windows, Linux or Mac computer to use with this project. I used a Windows PC, and thus I will be describing my experience from a Windows point of view. However, application to Linux or Mac should be straightforward if that's what you are using.

There are two purchases:
1 - Purchasing the Robot Car Kit
2 - Purchasing the extra electronic parts

In this section we will talk about purchasing the Robot Car kit.
Although I am in Canada, and although Osoyoo is actually based in Canada (although the robot kit parts are from China), it is much easier to order from the USA Amazon website:

Product title: OSOYOO Omni-directinal Mecanum Wheels Robotic Car Kit for Arduino Mega2560 Metal Chassis DC Motor DIY STEM Remote Controlled Educational Mechanical DIY Coding for Teens Adult
Product cost (at time of writing):  US$119.99   (plus about $25 to ship to Canada, but free shipping within USA if you have Prime)
link:  [amazon product link](https://www.amazon.com/OSOYOO-Omni-directinal-Controlled-Educational-Mechanical/dp/B0821DV5GJ/ref=sr_1_2?crid=1S643UFKFPI0E&keywords=osoyoo+omni+directional+mecanum+wheels+robot+car+kit+for+arduino&qid=1703129510&sprefix=osoyoo+omni-direction%2Caps%2C97&sr=8-2)

Troubleshooting note:  If you are able to allocate sufficient research funds, I would advise purchasing two kits so troubleshooting any issues with the hardware becomes easier. (Disclosure: I did not. I purchased a single kit with the expectation that I could get efficient Amazon.com delivery of a second kit should I need it.)

**Please purchase this exact model noted above** unless you want to make modifications to the code on your own.

In countries outside of Canada and USA, I would still recommend considering Amazon for easy delivery in certain countries where the Amazon service is efficient. In other countries consider the Osoyoo website:
[osoyoo website](https://osoyoo.com/)

Note: The Amazon website says this is a kit for teens while the Osoyoo website shows 5 years old building robotic kits (albeit simpler ones). Please keep in mind you are not buying this kit to produce a project for your high school science fair. You are buying this kit to have a grounded physical embodiment of an AI/AGI system which you then can use with tens of thousands lines of your Python code.



**Step #3 -- Purchase the extra electronic parts**

You may not need these extra navigation parts immediately, but since they are purchased from AliExpress and generally delivered from China via slow delivery means (given that the sum total of the parts is about US$30), you may want to order these parts once you decide to go ahead with the project.

I will provide the exact AliExpress link I used to purchase these extra navigation components:

[flight control sensor](https://www.aliexpress.com/item/1005003478577853.html?spm=a2g0o.order_detail.order_detail_item.3.1437f19cTglF4n)

[optional hex socket set screws](https://www.aliexpress.com/item/1005003699221015.html?spm=a2g0o.order_detail.order_detail_item.3.edeef19cPldfHc)

[optional board spacers](https://www.aliexpress.com/item/1005004818109229.html?spm=a2g0o.order_detail.order_detail_item.3.7b0cf19cGpkdzc)

[RGB sensor](https://www.aliexpress.com/item/1005003484925759.html?spm=a2g0o.order_detail.order_detail_item.3.4f67f19cQhDc0g)

[optional suspension modification](https://www.aliexpress.com/item/4001179419287.html?spm=a2g0o.order_detail.order_detail_item.4.4793f19cXElsA8)

Troubleshooting note:  If you are able to allocate sufficient research funds, I would advise purchasing two sets of electronic parts so troubleshooting any issues with the hardware becomes easier. (Disclosure: I did not.) 



**Step #4 -- Start to Build the Robot Car -- Finding the Documentation**

A few days (or day -- Amazon.com is very efficient) have gone by and a package arrives at your lab, office (or home perhaps). It's the Osoyoo robotic car kit.

Open the box, make sure that all the parts are there and are in good condition. (Mine were -- everything included and seemed brand new and in good condition.)

There is a cardboard sheet with a list of parts in Japanese -- you can use it and exercise your brain to learn some new symbols (assuming you don't read/write Japanese) and think about Harnad's concepts of symbols and grounding, e.g., [grounding problem](https://www.sciencedirect.com/science/article/abs/pii/S1389041722000493?via%3Dihub)

Or... you can turn the cardboard sheet over and read it in English :)
[Online link for this cardboard sheet of parts list in English](https://osoyoo.com/2019/11/08/omni-direction-mecanum-wheel-robotic-kit-v1/#4)

There will be a little manual with the car. It really only serves the purpose of telling you to go online and look at the manual(s) there:

[Osoyoo manual](https://osoyoo.com/?p=49235)

You will go to a busy webpage with all sorts of advertising scrolling by on the bottom, and possibly the top too. Just ignore this.
If you look at the center of the screen you will see a link to a PDF to download the PDF version of the manual -- do this so you can minimize the time spent on this website :)

Here is the link (although in case it changes, becomes updated, etc in the future you may want to go to the online manual link above):
[Useful PDF manual for Osoyoo robotic car kit](https://osoyoo.com/manual/202000600-m2.pdf)

Before we start constructing the robot car, take a look at some of the parts. There is a metal bottom chassis where the drive motors will be attached. On top of this metal bottom plate there will be a top acrylic plate. The electronics will all be mounted on this top acrylic plate.

Note that there is a separate drive motor for each of the four wheels. Note also there there is no steering apparatus. This is because these are Ilon Mecanum wheels that can go forwards and backwards, but also sideways.

![mecanum wheels directions of motion](mecanumwheel.png)

With regard to the electronics, note that there are three main electronics boards included. One of them is the motor driver board -- this board will control the motors attached to each wheel. Then there is the Mega2560 Arduino board. If you have not worked with Arduino before I will show you all the steps involved -- very easy. The Arduino board is the computer board essentially controlling the robotic car. Into the Arduino board there is a Wifi shield which will give the system Wifi access. There is a USB cable which plugs into the Arduino board and forms an easy to use interface with your laptop enabling you later to send your software to the Arduino board.

There are some smaller electronics boards also, e.g., tracking sensor module, etc. We will discuss them as we use them.

Note the blue lithium batteries. Note also a battery charger along with its cable which can charge these batteries.

Before we start building the robot car, let's have a quick look at the documentation (always a good idea no matter what project you are working on).

Please download the PDF rather than use the webpages with quasi-psychedelic advertisements flashing all over your screen. (After looking at the web pages, certainly at the time of this writing, you are wondering to yourself.... 'What kind of junk hardware is this?'  But, let me assure you, the hardware is not only cool but fairly well engineered. Ignore the webpages and download the manual, if you have not already done so.)
Link to download the PDF (ignore if you already downloaded it above): 
[Osoyoo manual](https://osoyoo.com/?p=49235)

The PDF Manual for the robot car is decent. Let's take a look at it.





**Step #5 -- Start to Build the Robot Car -- Mechanical Assembly**

Ok.... you have all the parts, you are somewhat familiar with the parts and you have downloaded the PDF manual. Let's start building....













