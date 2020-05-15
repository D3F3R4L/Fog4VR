/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright 2016 Technische Universitaet Berlin
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
#ifndef TCP_STREAM_CONTROLLER_H
#define TCP_STREAM_CONTROLLER_H

#include <ns3/core-module.h>
#include "ns3/application.h"
#include <iostream>
#include <fstream>
#include "ns3/log.h"
#include "ns3/nstime.h"
#include "ns3/simulator.h"
#include <stdint.h>
#include "tcp-stream-interface.h"
#include <stdexcept>
#include <assert.h>
#include <math.h>
#include <numeric>
#include <iomanip>
#include <string> 
#include <algorithm> 
#include <sstream> 
#include <iterator>
#include <stdlib.h>
#include <sstream>
#include <vector>



namespace ns3 {

struct serversData
{
  std::vector<bool> onOff;
  std::vector<double> memorySize;
  std::vector<double> memoryFree;
  std::vector< std::vector<uint16_t> > allocatedContentType;
  std::vector<Address> serverAddress;
  std::vector<double> cost;
};

extern serversData serverData;

void Controller (uint16_t numServers,uint16_t simId,std::string dir);

void serverInitialise (uint16_t serverId,double totalMemory,double freeMemory, std::vector<uint16_t> content, Address serverAddress, double cost);

void setOn (uint16_t serverId);

void setOff (uint16_t serverId);

void allocateMemory(uint16_t serverId,double size);

void desallocateMemory(uint16_t serverId,double size);

void addContent (uint16_t serverId,uint16_t content,double size);

void removeContent(uint16_t serverId,uint16_t content,double size);

void printInformation (uint16_t serverId);

std::pair <uint32_t, double> sendRequest (uint16_t content,double size,uint16_t clientId,uint16_t serverId,uint16_t pol);

void finishedRequest(uint16_t content,double size,uint16_t clientId,uint16_t serverId);

Address choiceServer (uint16_t content,double size,uint16_t clientId,uint16_t serverId);

void saveToLogFiles ();


}

#endif /* TCP_STREAM_CLIENT_H */
