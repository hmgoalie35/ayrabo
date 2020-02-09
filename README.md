# ayrabo
Sport scoresheets for the digital age

Dev: [![Build Status](https://travis-ci.org/hmgoalie35/ayrabo.svg?branch=dev)](https://travis-ci.org/hmgoalie35/ayrabo)

Prod: [![Build Status](https://travis-ci.org/hmgoalie35/ayrabo.svg?branch=master)](https://travis-ci.org/hmgoalie35/ayrabo)

# About
This is a personal/entrepreneurial project I had the idea for in college and started working on after graduating in May 2016. Having played club ice hockey for 4 years, I was always shocked at how painful it was to report game scores to the league. Team managers would have to call and tell the league the score of the game, and then manually enter in goals, assists, penalties, etc. on a website. I thought it would be a great idea to simply cut out all of this unneeded work. Cue ayrabo (name is a WIP). The goal is to provide a web based scoresheet that can facilitate keeping score for scorekeepers and keep everybody updated with the progress of the game. Every goal, assist, penalty, etc. for a given game is automatically synced to our servers, which allows us to live update our site to keep the game stats up to date. I aim to make this compatible with any sport, not just ice hockey. Users can even register as players/coaches/managers/referees for multiple sports and all of their stats will be available in one centralized location.

One potential problem is internet access in/on arenas, fields, etc. In this day and age it is becoming easier and easier to put up a wifi hotspot in the most unexpected places. My solution to this is an offline application that can by synced with our servers when the game is finished. Simply connect the device to the internet and voila. 

Right now the MVP I am aiming for is completely web browser based, and a computer or large tablet (really something with a large enough screen) with internet access is required. Future releases will potentially include a mac/windows/linux desktop application (Qt or Electron?) that can work with or without internet access and will tap into an API. This project will eventually be moved to a pure SOA so the front (Angular2?) and back ends can be completely separate.

A license has been intentionally excluded. See http://choosealicense.com/no-license/ for more information.

*nix system recommended, Linux VM will also suffice


# Development
  * Instructions are available [here](https://github.com/hmgoalie35/ayrabo/wiki/Setting-up-the-project-for-local-development)
