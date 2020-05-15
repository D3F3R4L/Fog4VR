/* Adapted from haraldott project
 * Author: fabioraraujo */
// - TCP Stream server and user-defined number of clients connected with an AP
// - WiFi connection
// - Tracing of throughput, packet information is done in the client

#include "ns3/point-to-point-helper.h"
#include <fstream>
#include "ns3/core-module.h"
#include "ns3/applications-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/network-module.h"
#include "ns3/wifi-module.h"
#include "ns3/mobility-module.h"
#include <ns3/buildings-module.h>
#include "ns3/building-position-allocator.h"
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>
#include "ns3/internet-apps-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/tcp-stream-helper.h"
#include "ns3/tcp-stream-interface.h"
#include <iostream>
#include <stdlib.h>
#include <sstream>
#include <iomanip>
#include <vector>
#include <string>

template <typename T>
std::string ToString(T val)
{
    std::stringstream stream;
    stream << val;
    return stream.str();
}

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("dash-migrationExample");

double StallMMESV1=0;
double RebufferMMESV1=0;
double StallMMESV2=0;
double RebufferMMESV2=0;
double StallMMESV3=0;
double RebufferMMESV3=0;
double StallMMECloud=0;
double RebufferMMECloud=0;
double StartMMESV1=0;
double StartMMESV2=0;
double StartMMESV3=0;
double StartMMECloud=0;
uint16_t n=3;
uint16_t MaxClientsSV=10;
uint32_t numberOfUeNodes;
uint32_t simulationId = 0;
std::vector <uint32_t> SClients {0,0,0,0};
std::vector <std::string> delays {"0","0","0","0"};
Address server1Address;
Address server2Address;
Address server3Address;
Address cloudAddress;

std::string dirTmp;
std::string type;
std::ofstream StallsLog;
std::ofstream RebufferLog;
std::ofstream StartTimeLog;
std::ofstream ServerScoreLog;

void
LogStall (uint16_t sv1,uint16_t sv2,uint16_t sv3,uint16_t cloud)
{
  StallsLog << std::setfill (' ') << std::setw (0) << Simulator::Now ().GetMicroSeconds ()  / (double)1000000 << ";"
              << std::setfill (' ') << std::setw (0) << sv1 << ";"
              << std::setfill (' ') << std::setw (0) << StallMMESV1 << ";"
              << std::setfill (' ') << std::setw (0) << sv2 << ";"
              << std::setfill (' ') << std::setw (0) << StallMMESV2 << ";"
              << std::setfill (' ') << std::setw (0) << sv3 << ";"
              << std::setfill (' ') << std::setw (0) << StallMMESV3 << ";"
              << std::setfill (' ') << std::setw (0) << cloud << ";"
              << std::setfill (' ') << std::setw (0) << StallMMECloud << ";\n";
  StallsLog.flush ();
}

void
LogRebuffer (double Tsv1,double Tsv2,double Tsv3,double Tcloud)
{
  RebufferLog << std::setfill (' ') << std::setw (0) << Simulator::Now ().GetMicroSeconds ()  / (double)1000000 << ";"
              << std::setfill (' ') << std::setw (0) << Tsv1 << ";"
              << std::setfill (' ') << std::setw (0) << RebufferMMESV1 << ";"
              << std::setfill (' ') << std::setw (0) << Tsv2 << ";"
              << std::setfill (' ') << std::setw (0) << RebufferMMESV2 << ";"
              << std::setfill (' ') << std::setw (0) << Tsv3 << ";"
              << std::setfill (' ') << std::setw (0) << RebufferMMESV3 << ";"
              << std::setfill (' ') << std::setw (0) << Tcloud << ";"
              << std::setfill (' ') << std::setw (0) << RebufferMMECloud << ";\n";
  RebufferLog.flush ();
}

void
LogStartTime (double sv1,double sv2,double sv3,double cloud)
{
  StartTimeLog << std::setfill (' ') << std::setw (0) << sv1 << ";"
              << std::setfill (' ') << std::setw (0) << StartMMESV1 << ";"
              << std::setfill (' ') << std::setw (0) << sv2 << ";"
              << std::setfill (' ') << std::setw (0) << StartMMESV2 << ";"
              << std::setfill (' ') << std::setw (0) << sv3 << ";"
              << std::setfill (' ') << std::setw (0) << StartMMESV3 << ";"
              << std::setfill (' ') << std::setw (0) << cloud << ";"
              << std::setfill (' ') << std::setw (0) << StartMMECloud << ";\n";
  StartTimeLog.flush ();
}
/*
void 
throughput(Ptr<FlowMonitor> flowMonitor,Ptr<Ipv4FlowClassifier> classifier)
{
  std::map<FlowId, FlowMonitor::FlowStats> stats = flowMonitor->GetFlowStats ();
  for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator iter = stats.begin (); iter != stats.end (); ++iter)
    {
      Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (iter->first);
      if (iter->second.rxPackets<=10 and (t.sourceAddress=="1.0.0.1" or t.sourceAddress=="2.0.0.1" or t.sourceAddress=="3.0.0.1"))
      {
          NS_LOG_UNCOND("Flow ID: " << iter->first << " Src Addr " << t.sourceAddress << " Dst Addr " << t.destinationAddress);
          NS_LOG_UNCOND("Tx Packets = " << iter->second.txPackets);
          //NS_LOG_UNCOND("Tx Bytes = " << iter->second.txBytes);
          //NS_LOG_UNCOND("Sum jitter = " << iter->second.jitterSum);
          //NS_LOG_UNCOND("Delay Sum = " << iter->second.delaySum);
          //NS_LOG_UNCOND("Lost Packet = " << iter->second.lostPackets);
          //NS_LOG_UNCOND("Rx Bytes = " << iter->second.rxBytes);
          NS_LOG_UNCOND("Rx Packets = " << iter->second.rxPackets);
          //NS_LOG_UNCOND("timeLastRxPacket = " << iter->second.timeLastRxPacket.GetSeconds());
          //NS_LOG_UNCOND("timefirstTxPacket = " << iter->second.timeFirstTxPacket.GetSeconds());
         // NS_LOG_UNCOND("Throughput: " << iter->second.rxBytes * 8.0 / (iter->second.timeLastRxPacket.GetSeconds()-iter->second.timeFirstTxPacket.GetSeconds()) / 1000/1000 << " Mbps");
          //NS_LOG_UNCOND("Packet loss %= " << ((iter->second.txPackets-iter->second.rxPackets)*1.0)/iter->second.txPackets);
      }
    }
  Simulator::Schedule(Seconds(1),&throughput,flowMonitor,classifier);
}
*/
void
getThropughputClients(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  for (uint i = 0; i < numberOfUeNodes; i++)
  {
    clientHelper.GetThroughput(clientApps, clients.at (i).first);
  }
  Simulator::Schedule(Seconds(1),&getThropughputClients,clientApps,clientHelper,clients);
}

void
getThropughputServer(ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  for (uint j = 0; j < servers.GetN(); j++)
  {
    serverHelper.serverThroughput(serverApp, servers.Get(j));
  }
  Simulator::Schedule(Seconds(1),&getThropughputServer,serverApp, serverHelper,servers);
}

void
getStall(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  uint16_t sv1=0;
  uint16_t sv2=0;
  uint16_t sv3=0;
  uint16_t cloud=0;
  double Tsv1=0;
  double Tsv2=0;
  double Tsv3=0;
  double Tcloud=0;
  NS_LOG_UNCOND("Stall");
  for (uint i = 0; i < numberOfUeNodes; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    if(ip=="1.0.0.1")
    {
      sv1+=clientHelper.GetNumbersOfBufferUnderrun(clientApps, clients.at (i).first);
      StallMMESV1=StallMMESV1 + (2*(sv1-StallMMESV1)/(n+1));
      Tsv1+=clientHelper.GetTotalBufferUnderrunTime(clientApps, clients.at (i).first);
      RebufferMMESV1=RebufferMMESV1 + (2*(Tsv1-RebufferMMESV1)/(n+1));
    }
    else
    {
      if(ip=="2.0.0.1")
      {
        sv2+=clientHelper.GetNumbersOfBufferUnderrun(clientApps, clients.at (i).first);
        StallMMESV2=StallMMESV2 + (2*(sv2-StallMMESV2)/(n+1));
        Tsv2+=clientHelper.GetTotalBufferUnderrunTime(clientApps, clients.at (i).first);
        RebufferMMESV2=RebufferMMESV2 + (2*(Tsv2-RebufferMMESV2)/(n+1));
      }
      else
      {
        if(ip=="3.0.0.1")
        {
          sv3+=clientHelper.GetNumbersOfBufferUnderrun(clientApps, clients.at (i).first);
          StallMMESV3=StallMMESV3 + (2*(sv3-StallMMESV3)/(n+1));
          Tsv3+=clientHelper.GetTotalBufferUnderrunTime(clientApps, clients.at (i).first);
          RebufferMMESV3=RebufferMMESV3 + (2*(Tsv3-RebufferMMESV3)/(n+1));
        }
        else
        {
          cloud+=clientHelper.GetNumbersOfBufferUnderrun(clientApps, clients.at (i).first);
          StallMMECloud=StallMMECloud + (2*(cloud-StallMMECloud)/(n+1));
          Tcloud+=clientHelper.GetTotalBufferUnderrunTime(clientApps, clients.at (i).first);
          RebufferMMECloud=RebufferMMECloud + (2*(Tcloud-RebufferMMECloud)/(n+1));
        }
      }
    }
  }
  LogStall(sv1,sv2,sv3,cloud);
  LogRebuffer(Tsv1,Tsv2,Tsv3,Tcloud);
  Simulator::Schedule(Seconds(1),&getStall,clientApps,clientHelper,clients);
}

static void
ServerHandover(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, Address server2Address, std::vector <std::pair <Ptr<Node>, std::string> > clients, uint16_t n)
{
  clientHelper.Handover(clientApps, clients.at (n).first, server2Address);
}

void
getStartTime(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  double sv1=0;
  double sv2=0;
  double sv3=0;
  double cloud=0;
  for (uint i = 0; i < numberOfUeNodes; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    if(ip=="1.0.0.1")
    {
      sv1+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
      StartMMESV1=StartMMESV1 + (2*(sv1-StartMMESV1)/(n+1));
    }
    else
    {
      if(ip=="2.0.0.1")
      {
        sv2+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
        StartMMESV2=StartMMESV2 + (2*(sv1-StartMMESV2)/(n+1));
      }
      else
      {
        if(ip=="3.0.0.1")
        {
          sv3+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
          StartMMESV3=StartMMESV3 + (2*(sv1-StartMMESV3)/(n+1));
        }
        else
        {
          cloud+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
          StartMMECloud=StartMMECloud + (2*(sv1-StartMMECloud)/(n+1));
        }
      }
    }
  }
  LogStartTime(sv1,sv2,sv3,cloud);
}

void
InitializeLogFiles (std::string dashLogDirectory, std::string m_algoName,std::string numberOfUeNodes, std::string simulationId)
{
  NS_LOG_UNCOND("Inicializando log");
  std::string SLog = dashLogDirectory + m_algoName + "/" +  numberOfUeNodes  + "/sim" + simulationId + "_" + "StallLog.csv";
  StallsLog.open (SLog.c_str ());
  StallsLog << "Time_Now;SV1_Stalls;SV1_Stalls_MME;SV2_Stalls;SV2_Stalls_MME;SV3_Stalls;SV3_Stalls_MME;Cloud_Stalls;Cloud_Stalls_MME\n";
  StallsLog.flush ();

  std::string RLog = dashLogDirectory + m_algoName + "/" +  numberOfUeNodes  + "/sim" + simulationId + "_" + "RebufferLog.csv";
  RebufferLog.open (RLog.c_str ());
  RebufferLog << "Time_Now;SV1_Rebuffer;SV1_Rebuffer_MME;SV2_Rebuffer;SV2_Rebuffer_MME;SV3_Rebuffer;SV3_Rebuffer_MME;Cloud_Rebuffer;Cloud_Rebuffer_MME\n";
  RebufferLog.flush ();

  std::string STLog = dashLogDirectory + m_algoName + "/" +  numberOfUeNodes  + "/sim" + simulationId + "_" + "PlaybackStartTime.csv";
  StartTimeLog.open (STLog.c_str ());
  StartTimeLog << "SV1_PlaybackStartTime;SV1_PlaybackStartTime_MME;SV2_PlaybackStartTime;SV2_PlaybackStartTime_MME;SV3_PlaybackStartTime;SV3_PlaybackStartTime_MME;Cloud_PlaybackStartTime;Cloud_PlaybackStartTime_MME\n";
  StartTimeLog.flush ();

  std::string SsLog = dashLogDirectory + m_algoName + "/" +  numberOfUeNodes  + "/sim" + simulationId + "_" + "ServerScores.csv";
  ServerScoreLog.open (SsLog.c_str ());
  ServerScoreLog << "SV1_Score;SV2_Score;SV3_Score;Cloud_Score;\n";
  ServerScoreLog.flush ();

}

void 
stopSim (TcpStreamClientHelper clientHelper, NodeContainer staContainer)
{
  uint32_t closedApps = 0;
  closedApps = clientHelper.checkApps(staContainer);
  if (closedApps>=numberOfUeNodes)
  {
    Simulator::Stop();
  }
  else
  {
    Simulator::Schedule(Seconds(5),&stopSim,clientHelper, staContainer);    
  }
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

void
getClientsOnServer(ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  for (uint j = 0; j < servers.GetN(); j++)
  {
    SClients[j]=serverHelper.numberOfUeNodes(serverApp, servers.Get(j));
    NS_LOG_UNCOND(SClients[j]);
  }
  if (SClients[0]==0 and SClients[1]==0 and SClients[2]==0 and SClients[3]==0)
  {
    Simulator::Stop();
  }
}

void
politica(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients,ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  getClientsOnServer(serverApp, serverHelper, servers);
  std::string filename = "python3 src/dash-migration/AHP/AHP.py " + dirTmp +" "+ToString(simulationId)+" "+delays[0]+" "+delays[1]+" "+delays[2]+" "+delays[3];
  //std::string bestSv = execute(filename.c_str());
  std::string bestSv="1.0.0.1 2.0.0.1 3.0.0.1";
  system(filename.c_str());
  std::vector <std::string> BestServers;
  BestServers = split(bestSv.c_str(), " ");

  for (uint i = 0; i < numberOfUeNodes; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    for (uint j = 0; j < BestServers.size(); j++)
    {
      Address SvIp;
      uint32_t SvClients;
      uint16_t aux;
      switch(BestServers[j].at(0))
      {
        case '1':
          SvIp=server1Address;
          SvClients=SClients[0];
          aux=0;
          break;
        case '2':
          SvIp=server2Address;
          SvClients=SClients[1];
          aux=1;
          break;
        case '3':
          SvIp=server3Address;
          SvClients=SClients[2];
          aux=2;
          break;
      }
      if (ip==BestServers[j])
      {
        j=BestServers.size();
      }
      else
      {
        if(SvClients<MaxClientsSV)
        {
          std::cout << SvIp << "ServerId: \t" << i << " Cliente" << SClients[aux]<< std::endl;
          SClients[aux]=SClients[aux]+1;
          ServerHandover(clientApps, clientHelper, SvIp, clients,i);
          j=BestServers.size();
        }
      }
    }
  }
  Simulator::Schedule(Seconds(1),&politica,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
}

void
politica2(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients,ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  Address SvIp;
  uint16_t aux;
  for (uint i = 0; i < numberOfUeNodes; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    getClientsOnServer(serverApp, serverHelper, servers);
    std::string filename = "python3 src/dash-migration/Guloso-Aleatorio/exemplo.py " + dirTmp +" "+ToString(type)+" "+ ToString(SClients[0])+" "+ ToString(SClients[1])+" "+ ToString(SClients[2])+" "+ ToString(SClients[3])+" "+ip+" "+ToString(simulationId)+" "+delays[0]+" "+delays[1]+" "+delays[2]+" "+delays[3];
    std::string bestSv = execute(filename.c_str());
    //std::string bestSv="1.0.0.1 2.0.0.1 3.0.0.1";
    //system(filename.c_str());
    std::vector <std::string> BestServers;
    BestServers = split(bestSv.c_str(), " ");
    switch(BestServers[0].at(0))
    {
      case '1':
        SvIp=server1Address;
        aux=0;
        break;
      case '2':
        SvIp=server2Address;
        aux=1;
        break;
      case '3':
        SvIp=server3Address;
        aux=2;
        break;
      default:
        SvIp=cloudAddress;
        aux=3;
        break;
    }
    if (ip!=BestServers[0])
    {
      std::cout << SvIp << "ServerId: \t" << i << " Cliente" << SClients[aux]<< std::endl;
      ServerHandover(clientApps, clientHelper, SvIp, clients,i);
    }
  }
  Simulator::Schedule(Seconds(1),&politica2,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
}

static void
PingRtt (std::string context, Time rtt)
{
  std::vector <std::string> nodes;
  nodes = split(context.c_str(), "/");
  delays[std::stoi(nodes[4])]=ToString(rtt);
  std::cout << context << " " << ToString(rtt) << std::endl;
}

int
main (int argc, char *argv[])
{

  uint64_t segmentDuration = 2000000;
  // The simulation id is used to distinguish log file results from potentially multiple consequent simulation runs.
  simulationId = 1;
  numberOfUeNodes = 4;
  uint16_t numberOfEnbNodes = 1;
  uint32_t numberOfServers = 4;
  std::string adaptationAlgo = "festive";
  std::string segmentSizeFilePath = "src/dash-migration/dash/segmentSizesBigBuck1A.txt";
  bool shortGuardInterval = true;
  int seedValue = 1;
  uint16_t pol=0;

  //lastRx=[numberOfUeNodes];

  CommandLine cmd;
  cmd.Usage ("Simulation of streaming with DASH.\n");
  cmd.AddValue ("simulationId", "The simulation's index (for logging purposes)", simulationId);
  cmd.AddValue ("numberOfUeNodes", "The number of clients", numberOfUeNodes);
  cmd.AddValue ("numberOfEnbNodes", "The number of ENB nodes", numberOfEnbNodes);
  cmd.AddValue ("segmentDuration", "The duration of a video segment in microseconds", segmentDuration);
  cmd.AddValue ("adaptationAlgo", "The adaptation algorithm that the client uses for the simulation", adaptationAlgo);
  cmd.AddValue ("segmentSizeFile", "The relative path (from ns-3.x directory) to the file containing the segment sizes in bytes", segmentSizeFilePath);
  cmd.AddValue("seedValue", "random seed value.", seedValue);
  cmd.AddValue("politica", "value to choose the type of politica to be used (0 is AHP , 1 is Greedy, 2 is random and 3 is none. Default is 3)", pol);
  cmd.Parse (argc, argv);

  RngSeedManager::SetSeed(seedValue + 10000);
  srand(seedValue);

  Config::SetDefault ("ns3::LteUeNetDevice::DlEarfcn", UintegerValue (100));
  Config::SetDefault ("ns3::LteEnbNetDevice::DlEarfcn", UintegerValue (100));
  Config::SetDefault ("ns3::LteEnbNetDevice::UlEarfcn", UintegerValue (18100));
  
  Config::SetDefault ("ns3::LteEnbNetDevice::DlBandwidth", UintegerValue (50));
  Config::SetDefault ("ns3::LteEnbNetDevice::UlBandwidth", UintegerValue (50));

  Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue (1446));
  Config::SetDefault("ns3::TcpSocket::SndBufSize", UintegerValue (524288));
  Config::SetDefault("ns3::TcpSocket::RcvBufSize", UintegerValue (524288));

  Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
  Ptr<PointToPointEpcHelper>  epcHelper = CreateObject<PointToPointEpcHelper> ();
  lteHelper->SetEpcHelper (epcHelper);

  ConfigStore inputConfig;
  inputConfig.ConfigureDefaults();

  // parse again so you can override default values from the command line
  Ptr<Node> pgw = epcHelper->GetPgwNode ();
  

   // Create a single RemoteHost
  NodeContainer remoteHostContainer;
  remoteHostContainer.Create (numberOfServers);
  Ptr<Node> remoteHost = remoteHostContainer.Get (0);
  Ptr<Node> remoteHost2 = remoteHostContainer.Get (1);
  Ptr<Node> remoteHost3= remoteHostContainer.Get (2);
  Ptr<Node> remoteHost4= remoteHostContainer.Get (3);
  InternetStackHelper internet;
  internet.Install (remoteHostContainer);


  /* Set up WAN link between server node and access point*/
  PointToPointHelper p2p;
  p2p.SetDeviceAttribute ("DataRate", StringValue ("1Gb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("11ms"));
  NetDeviceContainer wanIpDevices;
  wanIpDevices = p2p.Install (remoteHost, pgw);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1Gb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("12ms"));
  NetDeviceContainer wanIpDevices2;
  wanIpDevices2 = p2p.Install (remoteHost2, remoteHost);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1Gb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("11ms"));
  NetDeviceContainer wanIpDevices3;
  wanIpDevices3 = p2p.Install (remoteHost3, remoteHost2);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1Gb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("96ms"));
  NetDeviceContainer wanIpDevices4;
  wanIpDevices4 = p2p.Install (remoteHost4, remoteHost3);


  /* Assign IP addresses */
  Ipv4AddressHelper address;
  Ipv4AddressHelper address2;
  Ipv4AddressHelper address3;
  Ipv4AddressHelper address4;

  /* IPs for WAN */
  address.SetBase ("1.0.0.0", "255.255.255.0");
  address2.SetBase ("2.0.0.0", "255.255.255.0");
  address3.SetBase ("3.0.0.0", "255.255.255.0");
  address4.SetBase ("4.0.0.0", "255.255.255.0");
  Ipv4InterfaceContainer wanInterface = address.Assign (wanIpDevices);
  Ipv4InterfaceContainer wanInterface2 = address2.Assign (wanIpDevices2);
  Ipv4InterfaceContainer wanInterface3 = address3.Assign (wanIpDevices3);
  Ipv4InterfaceContainer wanInterface4 = address4.Assign (wanIpDevices4);
  

server1Address = Address(wanInterface.GetAddress (0));
server2Address = Address(wanInterface2.GetAddress (0));
server3Address = Address(wanInterface3.GetAddress (0));
cloudAddress = Address(wanInterface4.GetAddress (0));

Ipv4StaticRoutingHelper ipv4RoutingHelper;
Ptr<Ipv4StaticRouting> remoteStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost->GetObject<Ipv4> ());
remoteStaticRouting->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
Ptr<Ipv4StaticRouting> remoteStaticRouting2 = ipv4RoutingHelper.GetStaticRouting (remoteHost2->GetObject<Ipv4> ());
remoteStaticRouting2->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
Ptr<Ipv4StaticRouting> remoteStaticRouting3 = ipv4RoutingHelper.GetStaticRouting (remoteHost3->GetObject<Ipv4> ());
remoteStaticRouting3->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
Ptr<Ipv4StaticRouting> remoteStaticRouting4 = ipv4RoutingHelper.GetStaticRouting (remoteHost4->GetObject<Ipv4> ());
remoteStaticRouting4->AddNetworkRouteTo (Ipv4Address ("7.0.0.0"), Ipv4Mask ("255.0.0.0"), 1);
/* Create Nodes */
NodeContainer UeNodes;
UeNodes.Create (numberOfUeNodes);

NodeContainer EnbNodes;
EnbNodes.Create (numberOfEnbNodes);

  std::vector <std::pair <Ptr<Node>, std::string> > clients;
  for (NodeContainer::Iterator i = UeNodes.Begin (); i != UeNodes.End (); ++i)
    {
      std::pair <Ptr<Node>, std::string> client (*i, adaptationAlgo);
      clients.push_back (client);
    }

//////////////////////////////////////////////////////////////////////////////////////////////////
//// Set up Building
//////////////////////////////////////////////////////////////////////////////////////////////////
  double roomHeight = 3;
  double roomLength = 6;
  double roomWidth = 5;
  uint32_t xRooms = 8;
  uint32_t yRooms = 3;
  uint32_t nFloors = 6;

  Ptr<Building> b = CreateObject <Building> ();
  b->SetBoundaries (Box ( 0.0, xRooms * roomWidth,
                          0.0, yRooms * roomLength,
                          0.0, nFloors * roomHeight));
  b->SetBuildingType (Building::Office);
  b->SetExtWallsType (Building::ConcreteWithWindows);
  b->SetNFloors (6);
  b->SetNRoomsX (8);
  b->SetNRoomsY (3);

  Vector posAp = Vector ( 1.0, 1.0, 1.0);
  // give the server node any position, it does not have influence on the simulation, it has to be set though,
  // because when we do: mobility.Install (networkNodes);, there has to be a position as place holder for the server
  // because otherwise the first client would not get assigned the desired position.
  Vector posServer = Vector (1.5, 1.5, 1.5);

  /* Set up positions of nodes (AP and server) */
  Ptr<ListPositionAllocator> positionAlloc = CreateObject<ListPositionAllocator> ();
  positionAlloc->Add (posAp);
  positionAlloc->Add (posServer);


  Ptr<RandomRoomPositionAllocator> randPosAlloc = CreateObject<RandomRoomPositionAllocator> ();
  randPosAlloc->AssignStreams (simulationId);

  // create folder so we can log the positions of the clients
  const char * mylogsDir = dashLogDirectory.c_str();
  mkdir (mylogsDir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  std::string tobascoDirTmp = dashLogDirectory + adaptationAlgo + "/";
  const char * tobascoDir = tobascoDirTmp.c_str();
  //const char * tobascoDir = (ToString (dashLogDirectory) + ToString (adaptationAlgo) + "/").c_str();
  mkdir (tobascoDir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  dirTmp = dashLogDirectory + adaptationAlgo + "/" + ToString (numberOfUeNodes) + "/";
  //const char * dir = (ToString (dashLogDirectory) + ToString (adaptationAlgo) + "/" + ToString (numberOfUeNodes) + "/").c_str();
  const char * dir = dirTmp.c_str();
  mkdir(dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);

  std::cout << mylogsDir << "\n";
  std::cout << tobascoDir << "\n";
  std::cout << dir << "\n";

  std::ofstream clientPosLog;
  std::string clientPos = dashLogDirectory + adaptationAlgo + "/" + ToString (numberOfUeNodes) + "/" + "sim" + ToString (simulationId) + "_"  + "clientPos.txt";
  clientPosLog.open (clientPos.c_str());
  std::cout << clientPos << "\n";
  NS_ASSERT_MSG (clientPosLog.is_open(), "Couldn't open clientPosLog file");

  // allocate clients to positions
  for (uint i = 0; i < numberOfUeNodes; i++)
    {
      Vector pos = Vector (randPosAlloc->GetNext());
      positionAlloc->Add (pos);

      // log client positions
      clientPosLog << ToString(pos.x) << ", " << ToString(pos.y) << ", " << ToString(pos.z) << "\n";
      clientPosLog.flush ();
    }


  MobilityHelper mobility;
  mobility.SetPositionAllocator (positionAlloc);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (EnbNodes);
  BuildingsHelper::Install (EnbNodes);
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (UeNodes);
  BuildingsHelper::Install (UeNodes);
  BuildingsHelper::MakeMobilityModelConsistent ();

  NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice (EnbNodes);
  NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice (UeNodes);

  // Install the IP stack on the UEs
  internet.Install (UeNodes);
  Ipv4InterfaceContainer ueIpIface;
  ueIpIface = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueLteDevs));

  for (uint32_t u = 0; u < UeNodes.GetN (); ++u)
    {
      Ptr<Node> ueNode = UeNodes.Get (u);
      // Set the default gateway for the UE
      Ptr<Ipv4StaticRouting> ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ueNode->GetObject<Ipv4> ());
      ueStaticRouting->SetDefaultRoute (epcHelper->GetUeDefaultGatewayAddress (), 1);
    }

  // Attach one UE per eNodeB
  lteHelper->Attach(ueLteDevs);

  uint16_t port= 9;

  V4PingHelper ping = V4PingHelper (wanInterface.GetAddress (0));
  ApplicationContainer apps = ping.Install (EnbNodes.Get(0));
  V4PingHelper ping2 = V4PingHelper (wanInterface2.GetAddress (0));
  apps.Add(ping2.Install (EnbNodes.Get(0)));
  V4PingHelper ping3 = V4PingHelper (wanInterface3.GetAddress (0));
  apps.Add(ping3.Install (EnbNodes.Get(0)));
  V4PingHelper ping4 = V4PingHelper (wanInterface4.GetAddress (0));
  apps.Add(ping4.Install (EnbNodes.Get(0)));
  apps.Start (Seconds (2.0));

  // finally, print the ping rtts.
  Config::Connect ("/NodeList/*/ApplicationList/*/$ns3::V4Ping/Rtt",MakeCallback (&PingRtt));

  //Packet::EnablePrinting ();

  NodeContainer servers;
  servers.Add(remoteHost);
  servers.Add(remoteHost2);
  servers.Add(remoteHost3);
  servers.Add(remoteHost4);
  TcpStreamServerHelper serverHelper (port,simulationId,dirTmp); //NS_LOG_UNCOND("dash Install 277");
  serverHelper.SetAttribute ("RemoteAddress", AddressValue (server1Address));
  ApplicationContainer serverApp = serverHelper.Install (remoteHost);//NS_LOG_UNCOND("dash Install 278");
  serverHelper.SetAttribute ("RemoteAddress", AddressValue (server2Address));
  serverApp = serverHelper.Install (remoteHost2);
  serverHelper.SetAttribute ("RemoteAddress", AddressValue (server3Address));
  serverApp = serverHelper.Install (remoteHost3);
  serverHelper.SetAttribute ("RemoteAddress", AddressValue (cloudAddress));
  serverApp = serverHelper.Install (remoteHost4);
  serverApp.Start (Seconds (1.0));
  //serverApp2.Start (Seconds (1.0));
  //serverApp3.Start (Seconds (1.0));
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp0;
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp1;
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp2;
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp3;
  /*
  for (uint i = 0; i < numberOfUeNodes; i++)
    {
      if(i<numberOfUeNodes/4)
      {
        clients_temp0.push_back(clients[i]);
      }
      else 
        if(i<(2*numberOfUeNodes)/4)
          {
            clients_temp1.push_back(clients[i]);
          }
        else
          if(i<(3*numberOfUeNodes)/4)
          {
            clients_temp2.push_back(clients[i]);
          }
          else
          {
            clients_temp3.push_back(clients[i]);
          }
    }

  /* Install TCP/UDP Transmitter on the station */
  TcpStreamClientHelper clientHelper (server1Address, port);
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("numberOfUeNodes", UintegerValue(numberOfUeNodes));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (0));
  ApplicationContainer clientApps = clientHelper.Install (clients_temp0);

  //TcpStreamClientHelper clientHelper2 (server2Address, port);
  clientHelper.SetAttribute ("RemoteAddress", AddressValue (server2Address));
  clientHelper.SetAttribute ("RemotePort", UintegerValue (port));
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("numberOfUeNodes", UintegerValue(numberOfUeNodes));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (1));
  clientApps.Add(clientHelper.Install (clients_temp1));

  //TcpStreamClientHelper clientHelper3 (server3Address, port);
  clientHelper.SetAttribute ("RemoteAddress", AddressValue (server3Address));
  clientHelper.SetAttribute ("RemotePort", UintegerValue (port));
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("numberOfUeNodes", UintegerValue(numberOfUeNodes));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (2));
  clientApps.Add(clientHelper.Install (clients_temp2));

  clientHelper.SetAttribute ("RemoteAddress", AddressValue (cloudAddress));
  clientHelper.SetAttribute ("RemotePort", UintegerValue (port));
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("numberOfUeNodes", UintegerValue(numberOfUeNodes));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (3));
  clientApps.Add(clientHelper.Install (clients_temp3));
  
  for (uint i = 0; i < clientApps.GetN (); i++)
    {
      double startTime = 2.0;
      clientApps.Get (i)->SetStartTime (Seconds (startTime));
    }

/*

  /* Install TCP Receiver on the access point */
/*
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp0;
  clients_temp0.push_back(clients[0]);*/

  /* Install TCP/UDP Transmitter on the station */
  //TcpStreamClientHelper clientHelper (serverAddress, port); //NS_LOG_UNCOND("dash Install 288");
  //clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  //clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  //clientHelper.SetAttribute ("numberOfUeNodes", UintegerValue(numberOfUeNodes));
  //clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId)); //NS_LOG_UNCOND("dash Install 292");
  //ApplicationContainer clientApps = clientHelper.Install (clients); //NS_LOG_UNCOND("dash Install 293");


/*
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp1;
  clients_temp1.push_back(clients[1]);

  TcpStreamClientHelper clientHelper2 (serverAddress2, port);
  clientHelper2.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper2.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper2.SetAttribute ("numberOfUeNodes", UintegerValue(numberOfUeNodes));
  clientHelper2.SetAttribute ("SimulationId", UintegerValue (simulationId+1));
  ApplicationContainer clientApps2 = clientHelper2.Install (clients_temp1);*/
  //for (uint i = 0; i < clientApps.GetN (); i++)
    //{
      //double startTime = 2.0 + ((i * 3) / 100.0);
      //clientApps.Get (i)->SetStartTime (Seconds (startTime));
    //}
  /*
  for (uint i = 0; i < clientApps2.GetN (); i++)
    {
      double startTime = 2.0 + ((i * 3) / 100.0);
      clientApps2.Get (i)->SetStartTime (Seconds (startTime)); 
    }*/

  //Ptr<FlowMonitor> flowMonitor;
  //FlowMonitorHelper flowHelper;
  //flowMonitor = flowHelper.InstallAll();
  //Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier> (flowHelper.GetClassifier ());

  if (pol==0)
  {
  	Simulator::Schedule(Seconds(5.001),&politica,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
  }
  else
  {
  	if (pol==1)
  	{
  		type="guloso";
  		Simulator::Schedule(Seconds(5.001),&politica2,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
  	}
  	else
  	{
  	  if (pol==2)
  	  {
  		type="aleatorio";
  		Simulator::Schedule(Seconds(5.001),&politica2,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
  	  }
  	}
  }
  
  InitializeLogFiles (dashLogDirectory, adaptationAlgo,ToString(numberOfUeNodes),ToString(simulationId));

  NS_LOG_INFO ("Run Simulation.");
  NS_LOG_INFO ("Sim: " << simulationId << "Clients: " << numberOfUeNodes);
  //NS_LOG_UNCOND("SERVER1"<< serverAddress);
  //NS_LOG_UNCOND("SERVER2"<< serverAddress2);
  //Simulator::Schedule(Seconds(5),&ServerHandover,clientApps, clientHelper, server2Address, clients,0);
  //Simulator::Schedule(Seconds(1.05),&ServerHandover,clientApps, clientHelper, server2Address, clients,1);
  //Simulator::Schedule(Seconds(1.1),&ServerHandover,clientApps, clientHelper, server2Address, clients,2);
  //Simulator::Schedule(Seconds(1.15),&ServerHandover,clientApps, clientHelper, server2Address, clients,3);
  //Simulator::Schedule(Seconds(1.2),&ServerHandover,clientApps, clientHelper, server2Address, clients,4);
  //Simulator::Schedule(Seconds(1),&ServerHandover,clientApps, clientHelper, server3Address, clients,5);
  //Simulator::Schedule(Seconds(1.05),&ServerHandover,clientApps, clientHelper, server3Address, clients,6);
  //Simulator::Schedule(Seconds(1.1),&ServerHandover,clientApps, clientHelper, server3Address, clients,7);
  //Simulator::Schedule(Seconds(1.15),&ServerHandover,clientApps, clientHelper, server3Address, clients,8);
  //Simulator::Schedule(Seconds(1.2),&ServerHandover,clientApps, clientHelper, server3Address, clients,9);
  Simulator::Schedule(Seconds(2),&getThropughputServer,serverApp, serverHelper,servers);
  Simulator::Schedule(Seconds(2),&getThropughputClients,clientApps,clientHelper,clients);
  Simulator::Schedule(Seconds(3),&getStall,clientApps,clientHelper,clients);
  //Simulator::Schedule(Seconds(5),&stopSim,clientHelper,staContainer);
  Simulator::Schedule(Seconds(10),&getStartTime,clientApps,clientHelper,clients);
  //Simulator::Schedule(Seconds(1),&throughput,flowMonitor,classifier);
  Simulator::Run ();
  //flowMonitor->SerializeToXmlFile ("results.xml" , true, true );
  Simulator::Destroy ();
  NS_LOG_INFO ("Done.");

}
