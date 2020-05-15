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
#include <iomanip>
#include <string> 
#include <algorithm> 
#include <sstream> 
#include <iterator> 
#include "tcp-stream-controller.h"

template <typename T>
std::string ToString (T val)
{
  std::stringstream stream;
  stream << val;
  return stream.str ();
}

std::string 
execute(const char* cmd) 
{
    FILE* pipe = popen(cmd, "r");
    if (!pipe) return "ERROR";
    char buffer[128];
    std::string result = "";
    while(!feof(pipe)) {
        if(fgets(buffer, 128, pipe) != NULL)
            result += buffer;
    }
    pclose(pipe);
        if (result.size() > 0){
    result.resize(result.size()-1);
    }
    NS_LOG_UNCOND(result);
    return result;
}

std::vector <std::string>
split(const char *phrase, std::string delimiter){
    std::vector <std::string> list;
    std::string s = ToString (phrase);
    size_t pos = 0;
    std::string token;
    while ((pos = s.find(delimiter)) != std::string::npos) {
        token = s.substr(0, pos);
        list.push_back(token);
        s.erase(0, pos + delimiter.length());
    }
    list.push_back(s);
    return list;
}

namespace ns3 {

serversData serverData;
uint16_t nServers;
uint16_t simulationId;
std::string directory;
std::ofstream controllerLog;


void 
Controller (uint16_t numServers,uint16_t simId,std::string dir)
{
  serverData.onOff.reserve(numServers);
  serverData.onOff.resize(numServers);
  serverData.memorySize.reserve(numServers);
  serverData.memorySize.resize(numServers);
  serverData.memoryFree.reserve(numServers);
  serverData.memoryFree.resize(numServers);
  serverData.allocatedContentType.reserve(numServers);
  serverData.allocatedContentType.resize(numServers);
  serverData.serverAddress.reserve(numServers);
  serverData.serverAddress.resize(numServers);
  serverData.cost.reserve(numServers);
  serverData.cost.resize(numServers);
  nServers=numServers;
  simulationId=simId;
  directory=dir;
}

void 
serverInitialise (uint16_t serverId,double totalMemory,double freeMemory, std::vector<uint16_t> content, Address serverAddress, double cost)
{
  serverData.onOff.at(serverId)=0;
  serverData.memorySize.at(serverId)=totalMemory;
  serverData.memoryFree.at(serverId)=freeMemory;
  serverData.allocatedContentType.at(serverId)=content;
  serverData.serverAddress.at(serverId)=serverAddress;
  serverData.cost.at(serverId)=cost;
}

void
setOn (uint16_t serverId)
{
  serverData.onOff.at(serverId)=1;
}

void
setOff (uint16_t serverId)
{
  serverData.onOff.at(serverId)=0;
}

void
allocateMemory(uint16_t serverId,double size)
{
  double freeMem=serverData.memoryFree.at(serverId);
  serverData.memoryFree.at(serverId)=freeMem-size;
}

void
desallocateMemory(uint16_t serverId,double size)
{
  double freeMem=serverData.memoryFree.at(serverId);
  serverData.memoryFree.at(serverId)=freeMem+size;
}

void
addContent (uint16_t serverId,uint16_t content,double size)
{
  allocateMemory(serverId,size);
  serverData.allocatedContentType.at(serverId).push_back(content);
  saveToLogFiles ();
}

void
removeContent(uint16_t serverId,uint16_t content,double size)
{
  desallocateMemory(serverId,size);
  auto it = std::find(serverData.allocatedContentType.at(serverId).begin(), serverData.allocatedContentType.at(serverId).end(), content);
  int index=distance(serverData.allocatedContentType.at(serverId).begin(), it);
  serverData.allocatedContentType.at(serverId).erase(serverData.allocatedContentType.at(serverId).begin()+index);
  setOff(serverId);
  saveToLogFiles ();
}

void
printInformation (uint16_t serverId)
{
  std::cout << "ServerId:  " << serverId << std::endl;
  std::cout << "Total Memory:  " << serverData.memorySize.at(serverId) << std::endl;
  std::cout << "Free Memory:  " << serverData.memoryFree.at(serverId) << std::endl;
  std::cout << "Server Address:  " << Ipv4Address::ConvertFrom(serverData.serverAddress.at(serverId))<< std::endl;
  std::cout << "Content Id Allocated:" << ' ';
  for(uint16_t i=0; i<serverData.allocatedContentType.at(serverId).size(); ++i)
  {
    std::cout << serverData.allocatedContentType.at(serverId)[i] << ' ';
    if (i==serverData.allocatedContentType.at(serverId).size()-1)
    {
      std::cout << ' ' << std::endl;
    }
  }
}

std::pair <uint32_t, double> 
sendRequest (uint16_t content,double size,uint16_t clientId,uint16_t serverId,uint16_t pol)
{
  saveToLogFiles ();
  std::pair <uint32_t, double> resp;
  //AHP
  if(pol==4 or pol==7)
  {
    std::string filename = "python3 src/Fog4MS/AHP/AHP.py " + directory +" "+ToString(simulationId) +" "+ToString(size)+" "+ToString(serverId)+" "+ToString(content);
    std::string ahp = execute(filename.c_str());
    std::vector <std::string> Ahp;
    //system(filename.c_str());
    //std::string ahp="5 3";
    Ahp = split(ahp.c_str(), " ");
    resp.first=std::stoul(Ahp[0]);
    resp.second=std::stod(Ahp[1]);
  }
  if (pol==5)
  {
    std::string filename = "python3 src/Fog4MS/Guloso-Aleatorio/exemplo.py " + directory +" "+ToString(simulationId) +" "+ToString(size)+" "+ToString(serverId)+" "+ToString(content)+" "+"guloso";
    std::string ahp = execute(filename.c_str());
    std::vector <std::string> Ahp;
    //system(filename.c_str());
    //std::string ahp="5 3";
    Ahp = split(ahp.c_str(), " ");
    resp.first=std::stoul(Ahp[0]);
    resp.second=std::stod(Ahp[1]);
  }
  if (pol==6)
  {
    std::string filename = "python3 src/Fog4MS/Guloso-Aleatorio/exemplo.py " + directory +" "+ToString(simulationId) +" "+ToString(size)+" "+ToString(serverId)+" "+ToString(content)+" "+"ale";
    std::string ahp = execute(filename.c_str());
    std::vector <std::string> Ahp;
    //system(filename.c_str());
    Ahp = split(ahp.c_str(), " ");
    resp.first=std::stoul(Ahp[0]);
    resp.second=std::stod(Ahp[1]);
  }
  if (pol==7)
  {
    resp.first=7;
    resp.second=0;
  }
  if (pol==8)
  {
    std::string filename = "python3 src/Fog4MS/PLI/pliLocal.py " + directory +" "+ToString(simulationId) +" "+ToString(size)+" "+ToString(serverId)+" "+ToString(content)+" "+ToString(clientId);
    std::string ahp = execute(filename.c_str());
    std::vector <std::string> Ahp;
    //system(filename.c_str());
    Ahp = split(ahp.c_str(), " ");
    resp.first=std::stoul(Ahp[0]);
    resp.second=std::stod(Ahp[1]);
  }
  //resp.first=5;
  //resp.second=4.72;
  NS_LOG_UNCOND(resp.first);
  NS_LOG_UNCOND(resp.second);
  //resp.second=(524288/resp.second)/(1000*8);
  //resp.second=size/(20*resp.second);
  return resp;
}

void
finishedRequest(uint16_t content,double size,uint16_t clientId,uint16_t serverId)
{
  removeContent(serverId,content,size);
  printInformation (serverId);
}

Address 
choiceServer (uint16_t content,double size,uint16_t clientId,uint16_t serverId)
{
  if (!serverData.onOff.at(serverId))
  {
    NS_LOG_UNCOND("Server ON");
    setOn(serverId);
  }
  addContent(serverId,content,size);
  printInformation (serverId);
  return serverData.serverAddress.at(serverId);
  std::vector<uint16_t> OnSvIds;
  std::vector<uint16_t> OffSvIds;
  std::vector<uint16_t> SvIds;
  for (uint i = 0; i < nServers; i++)
  {
    std::vector<uint16_t> vec = serverData.allocatedContentType.at(i);
    if(serverData.onOff.at(i))
    {
      OnSvIds.push_back(i);
    }
    else
    {
      OffSvIds.push_back(i);
    }  
  }
  for(uint j=0; j<OnSvIds.size();j++)
  {
    std::vector<uint16_t> vec = serverData.allocatedContentType.at(j);
    if(std::find(vec.begin(), vec.end(), content) != vec.end())
    {
      SvIds.push_back(j);
    }
  }
  if (SvIds.size()!=0)
  {
    addContent(SvIds[0],content,size);
    printInformation (SvIds[0]);
    return serverData.serverAddress.at(SvIds[0]);
  }
  else
  {
    addContent(0,content,size);
    printInformation (0);
    return serverData.serverAddress.at(0);
  }
}

void  
saveToLogFiles ()
{
  std::string cLog = directory + "Controller"+ "_sim" + ToString(simulationId) +"_" +"Log.csv";
  controllerLog.open (cLog.c_str ());
  controllerLog << "OnOff;TotalMemory;FreeMemory;ServerAddress;AllocatedContent\n";
  controllerLog.flush ();
  for(uint16_t i=0; i<nServers; ++i)
  {
    std::ostringstream vts;
    if(!serverData.allocatedContentType.at(i).empty())
    {
      std::copy(serverData.allocatedContentType.at(i).begin(), serverData.allocatedContentType.at(i).end()-1,std::ostream_iterator<int>(vts, "/"));
      vts << serverData.allocatedContentType.at(i).back();
    }
    controllerLog << std::setfill (' ') << std::setw (0) << serverData.onOff.at(i) << ";"
                  << std::setfill (' ') << std::setw (0) << serverData.memorySize.at(i) << ";"
                  << std::setfill (' ') << std::setw (0) << serverData.memoryFree.at(i) << ";"
                  << std::setfill (' ') << std::setw (0) << Ipv4Address::ConvertFrom(serverData.serverAddress.at(i)) << ";"
                  << std::setfill (' ') << std::setw (0) << vts.str() << ";\n";
    /*for(uint16_t j=0; j<serverData.allocatedContentType.at(i).size(); ++j)
    {
      if (i==serverData.allocatedContentType.at(i).size()-1)
      {
        controllerLog << std::setfill (' ') << std::setw (0) << serverData.allocatedContentType.at(i)[j] << ";\n";
      }
      else
      {
        controllerLog << std::setfill (' ') << std::setw (0) << serverData.allocatedContentType.at(i)[j] << ";";
      }
    }
    if (serverData.allocatedContentType.at(i).size()==0)
    {
      controllerLog << std::setfill (' ') << std::setw (0) << "\n";
    }*/
    controllerLog.flush ();
  }
  controllerLog.close();
}

} // namespace ns3