/* Adapted from haraldott project*/
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
#include "ns3/tcp-stream-controller.h"
#include <iostream>
#include <stdlib.h>
#include <sstream>
#include <iomanip>
#include <vector>
#include <string>
#include <iterator>
#include <random>

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
uint16_t MaxClientsSV=300;
uint32_t numberOfClients;
uint32_t simulationId = 0;
int seedValue;
std::vector <double> throughputs;
std::vector <double> Rebuffers;
std::vector <uint64_t> Stalls;
std::vector <uint32_t> SClients {0,0,0,0};
std::vector <uint32_t> SBClients {0,0,0,0};
std::vector <uint32_t> queue {0,0,0,0};
std::vector < std::vector<std::string> > delays(10,std::vector<std::string>(10));
std::vector <int> qualis {4,3,5,6,2,7,1,0};
std::vector <double> sizes {90,146.25,225,337.5,506.25,765,1057.5,1350};
//serversData teste;
Address PAAddress;
Address PEAddress;
Address MGAddress;
Address SPAddress;
std::vector< Ipv4Address > fogAddress; 
std::vector< Ipv4Address > pingAddress; 
std::vector< double > sum_probs;
std::vector< double > sum_probsQ;
std::string dirTmp;
std::string type;
std::ofstream StallsLog;
std::ofstream RebufferLog;
std::ofstream StartTimeLog;
std::ofstream ServerScoreLog;
std::ofstream ClientsLog;


double averageArrival = 0.4;
double lamda = 1 / averageArrival;
std::mt19937 rng (0);
std::exponential_distribution<double> poi (lamda);
std::uniform_int_distribution<> dis(0, 9);
std::uniform_real_distribution<double> unif(0, 1);

double sumArrivalTimes=3.6;
double newArrivalTime;

double
poisson()
{
  newArrivalTime=poi.operator() (rng);// generates the next random number in the distribution 
  sumArrivalTimes=sumArrivalTimes + newArrivalTime;  
  std::cout << "newArrivalTime:  " << newArrivalTime  << "    ,sumArrivalTimes:  " << sumArrivalTimes << std::endl;
  if (sumArrivalTimes<3.6)
  {
    sumArrivalTimes=3.6;
  }
  return sumArrivalTimes;
}

uint32_t 
uniformDis()
{
  uint32_t value=dis.operator() (rng);
  std::cout << "Ilha:  " << value << std::endl;
  return value;
}

int
zipf(double alpha, int n)
{
  static int first = true;      // Static first time flag
  static double c = 0;          // Normalization constant                 
  double z;                     // Uniform random number (0 < z < 1)
  int zipf_value;               // Computed exponential value to be returned
  int    i;                     // Loop counter
  int low, high, mid;           // Binary-search bounds

  // Compute normalization constant on first call only
  if (first == true)
  {
    sum_probs.reserve(n+1); // Pre-calculated sum of probabilities
    sum_probs.resize(n+1);
    for (i=1; i<=n; i++)
      c = c + (1.0 / pow((double) i, alpha));
    c = 1.0 / c;

    //sum_probs = malloc((n+1)*sizeof(*sum_probs));
    sum_probs[0] = 0;
    for (i=1; i<=n; i++) {
      sum_probs[i] = sum_probs[i-1] + c / pow((double) i, alpha);
    }
    first = false;
  }

  // Pull a uniform random number (0 < z < 1)
  do
  {
    z = unif.operator() (rng);
  }
  while ((z == 0) || (z == 1));
  //for (i=0; i<=n; i++)
  //{
  //  std::cout << "sum_probs:  " << sum_probs[i] << std::endl;
  //}
  //std::cout << "z:  " << z << std::endl;
  // Map z to the value
  low = 1, high = n, mid;
  do {
    mid = floor((low+high)/2);
    if (sum_probs[mid] >= z && sum_probs[mid-1] < z) {
      zipf_value = mid;
      break;
    } else if (sum_probs[mid] >= z) {
      high = mid-1;
    } else {
      low = mid+1;
    }
  } while (low <= high);
  std::cout << "ZIPF:  " << zipf_value << std::endl;
  // Assert that zipf_value is between 1 and N
  assert((zipf_value >=1) && (zipf_value <= n));
  return(zipf_value);
}

int
zipfQuality(double alpha, int n)
{ 
  static int first = true;      // Static first time flag
  static double c = 0;          // Normalization constant                 
  double z;                     // Uniform random number (0 < z < 1)
  int zipf_value;               // Computed exponential value to be returned
  int    i;                     // Loop counter
  int low, high, mid;           // Binary-search bounds

  // Compute normalization constant on first call only
  if (first == true)
  {
    sum_probsQ.reserve(n+1); // Pre-calculated sum of probabilities
    sum_probsQ.resize(n+1);
    for (i=1; i<=n; i++)
      c = c + (1.0 / pow((double) i, alpha));
    c = 1.0 / c;

    //sum_probs = malloc((n+1)*sizeof(*sum_probs));
    sum_probsQ[0] = 0;
    for (i=1; i<=n; i++) {
      sum_probsQ[i] = sum_probsQ[i-1] + c / pow((double) i, alpha);
    }
    first = false;
  }

  // Pull a uniform random number (0 < z < 1)
  do
  {
    z = unif.operator() (rng);
  }
  while ((z == 0) || (z == 1));
  
  //std::cout << "z:  " << z << std::endl;
  // Map z to the value
  low = 1, high = n, mid;
  do {
    mid = floor((low+high)/2);
    if (sum_probsQ[mid] >= z && sum_probsQ[mid-1] < z) {
      zipf_value = mid;
      break;
    } else if (sum_probsQ[mid] >= z) {
      high = mid-1;
    } else {
      low = mid+1;
    }
  } while (low <= high);
  std::cout << "ZIPFQuality:  " << zipf_value << std::endl;
  // Assert that zipf_value is between 1 and N
  assert((zipf_value >=1) && (zipf_value <= n));
  return(zipf_value);
}


void
LogStall (double sv1,double sv2,double sv3,double cloud)
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

void
LogClient (uint Id, uint32_t Location, int content, int contentQuality, double size, double startTime)
{
  ClientsLog  << std::setfill (' ') << std::setw (0) << Id << ";"
              << std::setfill (' ') << std::setw (0) << Location << ";"
              << std::setfill (' ') << std::setw (0) << content << ";"
              << std::setfill (' ') << std::setw (0) << contentQuality << ";"
              << std::setfill (' ') << std::setw (0) << size << ";"
              << std::setfill (' ') << std::setw (0) << startTime << ";\n";
  ClientsLog.flush ();
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
  for (uint i = 0; i < numberOfClients; i++)
  {
    throughputs[i]=clientHelper.GetThroughput(clientApps, clients.at (i).first);
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

static void
ServerHandover(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, Address server2Address, std::vector <std::pair <Ptr<Node>, std::string> > clients, uint16_t n)
{
  clientHelper.Handover(clientApps, clients.at (n).first, server2Address);
}

void
getStartTime(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  double STsv1=0;
  double STsv2=0;
  double STsv3=0;
  double STcloud=0;
  for (uint i = 0; i < numberOfClients; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    if(ip=="1.0.0.1")
    {
      STsv1+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
      StartMMESV1=StartMMESV1 + (2*(STsv1-StartMMESV1)/(n+1));
    }
    else
    {
      if(ip=="2.0.0.1")
      {
        STsv2+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
        StartMMESV2=StartMMESV2 + (2*(STsv2-StartMMESV2)/(n+1));
      }
      else
      {
        if(ip=="3.0.0.1")
        {
          STsv3+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
          StartMMESV3=StartMMESV3 + (2*(STsv2-StartMMESV3)/(n+1));
        }
        else
        {
          STcloud+=clientHelper.GetPlaybakStartTime(clientApps, clients.at (i).first);
          StartMMECloud=StartMMECloud + (2*(STcloud-StartMMECloud)/(n+1));
        }
      }
    }
  }
  LogStartTime(STsv1,STsv2,STsv3,STcloud);
}

void
InitializeLogFiles (std::string dashLogDirectory, std::string m_algoName,std::string numberOfClients, std::string simulationId,std::string pol)
{
  NS_LOG_UNCOND("Inicializando log");
  std::string SLog = dashLogDirectory + m_algoName + "/" +  numberOfClients  + "/" + pol + "/sim" + simulationId + "_" + "StallLog.csv";
  StallsLog.open (SLog.c_str ());
  StallsLog << "Time_Now;SV1_Stalls;SV1_Stalls_MME;SV2_Stalls;SV2_Stalls_MME;SV3_Stalls;SV3_Stalls_MME;Cloud_Stalls;Cloud_Stalls_MME\n";
  StallsLog.flush ();

  std::string RLog = dashLogDirectory + m_algoName + "/" +  numberOfClients + "/" + pol + "/sim" + simulationId + "_" + "RebufferLog.csv";
  RebufferLog.open (RLog.c_str ());
  RebufferLog << "Time_Now;SV1_Rebuffer;SV1_Rebuffer_MME;SV2_Rebuffer;SV2_Rebuffer_MME;SV3_Rebuffer;SV3_Rebuffer_MME;Cloud_Rebuffer;Cloud_Rebuffer_MME\n";
  RebufferLog.flush ();

  std::string STLog = dashLogDirectory + m_algoName + "/" +  numberOfClients + "/" + pol + "/sim" + simulationId + "_" + "PlaybackStartTime.csv";
  StartTimeLog.open (STLog.c_str ());
  StartTimeLog << "SV1_PlaybackStartTime;SV1_PlaybackStartTime_MME;SV2_PlaybackStartTime;SV2_PlaybackStartTime_MME;SV3_PlaybackStartTime;SV3_PlaybackStartTime_MME;Cloud_PlaybackStartTime;Cloud_PlaybackStartTime_MME\n";
  StartTimeLog.flush ();

  std::string SsLog = dashLogDirectory + m_algoName + "/" +  numberOfClients + "/" + pol + "/sim" + simulationId + "_" + "ServerScores.csv";
  ServerScoreLog.open (SsLog.c_str ());
  ServerScoreLog << "SV1_Score;SV2_Score;SV3_Score;Cloud_Score;\n";
  ServerScoreLog.flush ();

  std::string CLog = dashLogDirectory + m_algoName + "/" +  numberOfClients + "/" + pol + "/sim" + simulationId + "_" + "ClientsBegin.csv";
  ClientsLog.open (CLog.c_str ());
  ClientsLog << "ID;Location;ContentId;ContentQuality;ContentSize;StartTime\n";
  ClientsLog.flush ();
}

void 
stopSim (TcpStreamClientHelper clientHelper, NodeContainer staContainer)
{
  uint32_t closedApps = 0;
  closedApps = clientHelper.checkApps(staContainer);
  if (closedApps>=numberOfClients)
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
getStall(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  double sv1=0;
  double sv2=0;
  double sv3=0;
  double cloud=0;
  double Tsv1=0;
  double Tsv2=0;
  double Tsv3=0;
  double Tcloud=0;
  std::string filename = "python3 src/Fog4MS/StallRebuffer.py " + dirTmp +" "+ToString(simulationId);
  std::string Values = execute(filename.c_str());
  NS_LOG_UNCOND(Values);
  //system(filename.c_str());
  std::vector <std::string> StallsRebuffers;
  StallsRebuffers = split(Values.c_str(), " ");
  sv1+=std::stod(StallsRebuffers[0]);
  StallMMESV1=StallMMESV1 + (2*(sv1-StallMMESV1)/(n+1));
  Tsv1+=std::stod(StallsRebuffers[1]);
  RebufferMMESV1=RebufferMMESV1 + (2*(Tsv1-RebufferMMESV1)/(n+1));
  sv2+=std::stod(StallsRebuffers[2]);
  StallMMESV2=StallMMESV2 + (2*(sv2-StallMMESV2)/(n+1));
  Tsv2+=std::stod(StallsRebuffers[3]);
  RebufferMMESV2=RebufferMMESV2 + (2*(Tsv2-RebufferMMESV2)/(n+1));
  sv3+=std::stod(StallsRebuffers[4]);
  StallMMESV3=StallMMESV3 + (2*(sv3-StallMMESV3)/(n+1));
  Tsv3+=std::stod(StallsRebuffers[5]);
  RebufferMMESV3=RebufferMMESV3 + (2*(Tsv3-RebufferMMESV3)/(n+1));
  cloud+=std::stod(StallsRebuffers[6]);
  StallMMECloud=StallMMECloud + (2*(cloud-StallMMECloud)/(n+1));
  Tcloud+=std::stod(StallsRebuffers[7]);
  RebufferMMECloud=RebufferMMECloud + (2*(Tcloud-RebufferMMECloud)/(n+1));
  LogStall(sv1,sv2,sv3,cloud);
  LogRebuffer(Tsv1,Tsv2,Tsv3,Tcloud);
  Simulator::Schedule(Seconds(1),&getStall,clientApps,clientHelper,clients);
}

void
getClientsStallsRebuffers(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  for (uint i = 0; i < numberOfClients; i++)
  {
    Rebuffers[i]=clientHelper.GetTotalBufferUnderrunTime(clientApps, clients.at (i).first);
    Stalls[i]=clientHelper.GetNumbersOfBufferUnderrun(clientApps, clients.at (i).first);
  }
}

void
getClientsOnServer(ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  for (uint j = 0; j < servers.GetN(); j++)
  {
    SClients[j]=serverHelper.NumberOfClients(serverApp, servers.Get(j));
    NS_LOG_UNCOND(SClients[j]);
  }
  if (SClients[0]==0 and SClients[1]==0 and SClients[2]==0 and SClients[3]==0)
  {
    Simulator::Stop();
  }
}

void
getClientsHandover(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients)
{
  queue[0]=0;
  queue[1]=0;
  queue[2]=0;
  queue[3]=0;
  for (uint j = 0; j < numberOfClients; j++)
  {
    std::string ip;
    if (clientHelper.GetHandover(clientApps, clients.at (j).first))
    {
      ip=clientHelper.GetNewServerAddress(clientApps, clients.at (j).first);
      switch(ip.at(0))
      {
        case '1':
          queue[0]=queue[0]+1;
          break;
        case '2':
          queue[1]=queue[1]+1;
          break;
        case '3':
          queue[2]=queue[2]+1;
          break;
        case '4':
          queue[3]=queue[3]+1;
          break;
      }
    }
  }
  NS_LOG_UNCOND(queue[0]);
  NS_LOG_UNCOND(queue[1]);
  NS_LOG_UNCOND(queue[2]);
  NS_LOG_UNCOND(queue[3]);
}

uint64_t
getRepIndex(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, Ptr <Node> clients)
{
  return clientHelper.GetRepIndex(clientApps,clients);
}
/*
void
politica(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients,ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  getClientsOnServer(serverApp, serverHelper, servers);
  getClientsHandover(clientApps,clientHelper,clients);
  getClientsStallsRebuffers(clientApps,clientHelper,clients);
  double T1=0;
  double T2=0;
  double T3=0;
  double T4=0;
  uint16_t C1=0;
  uint16_t C2=0;
  uint16_t C3=0;
  uint16_t C4=0;
  for (uint i = 0; i < numberOfClients; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    switch(ip.at(0))
    {
      case '1':
        T1 = T1 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C1+=1;
        break;
      case '2':
        T2 = T2 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C2+=1;
        break;
      case '3':
        T3 = T3 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C3+=1;
        break;
      case '4':
        T4 = T4 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C4+=1;
        break;
    }
  }
  /*
  for (uint k = 0; k < 4; k++)
  {
    int dif=SClients[k]-SBClients[k];
    if (dif>0)
    {
      queue[k]=queue[k]-dif;
    }
  }
  for (uint i = 0; i < numberOfClients; i++)
  {
    NS_LOG_UNCOND(Stalls[i]);
    NS_LOG_UNCOND(Rebuffers[i]);
    NS_LOG_UNCOND(throughputs[i]);
    uint64_t Tc = getRepIndex(clientApps,clientHelper,clients.at (i).first);
    double Tf1 = (T1 + Tc);
    double Tf2 = (T2 + Tc);
    double Tf3 = (T3 + Tc);
    double Tf4 = (T4 + Tc);
    if (true) //Stalls[i]>=2 or Rebuffers[i]>=2
    {
      std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
      std::string filename = "python3 src/Fog4MS/AHP/AHP.py " + dirTmp +" "+ToString(simulationId)+" "+delays[0]+" "+delays[1]+" "+delays[2]+" "+delays[3]+" "+ip+" "+ToString(Tf1)+" "+ToString(Tf2)+" "+ToString(Tf3)+" "+ToString(Tf4);
      //std::string bestSv = execute(filename.c_str());
      std::string bestSv="1.0.0.1 2.0.0.1 3.0.0.1";
      system(filename.c_str());
      std::vector <std::string> BestServers;
      BestServers = split(bestSv.c_str(), " ");
      bool jump=false;
      for (uint j = 0; j < BestServers.size(); j++)
      {
        Address SvIp;
        uint16_t aux;
        switch(BestServers[j].at(0))
        {
          case '1':
            SvIp=PAAddress;
            T1=Tf1;
            aux=0;
            break;
          case '2':
            SvIp=PEAddress;
            T2=Tf2;
            aux=1;
            break;
          case '3':
            SvIp=MGAddress;
            T3=Tf3;
            aux=2;
            break;
          case '4':
            SvIp=SPAddress;
            T4=Tf4;
            aux=3;
            break;
          case '5':
            jump=true;
            break;
        }
        if (ip==BestServers[j] or jump)
        {
          j=BestServers.size();
        }
        else
        {
          if(SClients[aux]+queue[aux]<MaxClientsSV)
          {
            std::cout << SvIp << "ServerId: \t" << i << " Cliente" << SClients[aux]<< std::endl;
            queue[aux]=queue[aux]+1;
            ServerHandover(clientApps, clientHelper, SvIp, clients,i);
            j=BestServers.size();
          }
        }
      }
    }
  }
  for (uint l = 0; l < 4; l++)
  {
    SBClients[l]=SClients[l];
  }
  Simulator::Schedule(Seconds(2),&politica,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
}

void
politica2(ApplicationContainer clientApps, TcpStreamClientHelper clientHelper, std::vector <std::pair <Ptr<Node>, std::string> > clients,ApplicationContainer serverApp, TcpStreamServerHelper serverHelper,NodeContainer servers)
{
  getClientsOnServer(serverApp, serverHelper, servers);
  getClientsHandover(clientApps,clientHelper,clients);
  getClientsStallsRebuffers(clientApps,clientHelper,clients);
  double T1=0;
  double T2=0;
  double T3=0;
  double T4=0;
  uint16_t C1=0;
  uint16_t C2=0;
  uint16_t C3=0;
  uint16_t C4=0;
  for (uint i = 0; i < numberOfClients; i++)
  {
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    switch(ip.at(0))
    {
      case '1':
        T1 = T1 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C1+=1;
        break;
      case '2':
        T2 = T2 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C2+=1;
        break;
      case '3':
        T3 = T3 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C3+=1;
        break;
      case '4':
        T4 = T4 + getRepIndex(clientApps,clientHelper,clients.at (i).first);
        C4+=1;
        break;
    }
  }
  /*
  for (uint k = 0; k < 4; k++)
  {
    int dif=SClients[k]-SBClients[k];
    if (dif>0)
    {
      queue[k]=queue[k]-dif;
    }
  }
  for (uint i = 0; i < numberOfClients; i++)
  {
    NS_LOG_UNCOND(Stalls[i]);
    NS_LOG_UNCOND(Rebuffers[i]);
    NS_LOG_UNCOND(throughputs[i]);
    uint64_t Tc = getRepIndex(clientApps,clientHelper,clients.at (i).first);
    double Tf1 = (T1 + Tc);
    double Tf2 = (T2 + Tc);
    double Tf3 = (T3 + Tc);
    double Tf4 = (T4 + Tc);
    std::string ip = clientHelper.GetServerAddress(clientApps, clients.at (i).first);
    std::string filename = "python3 src/Fog4MS/Guloso-Aleatorio/exemplo.py " + dirTmp +" "+ToString(type)+" "+ ToString(SClients[0]+queue[0])+" "+ ToString(SClients[1]+queue[1])+" "+ ToString(SClients[2]+queue[2])+" "+ ToString(SClients[3])+" "+ip+" "+ToString(simulationId)+" "+delays[0]+" "+delays[1]+" "+delays[2]+" "+delays[3]+" "+ToString(throughputs[i])+" "+ToString(Stalls[i])+" "+ToString(Rebuffers[i])+" "+ToString(Tf1)+" "+ToString(Tf2)+" "+ToString(Tf3)+" "+ToString(Tf4);
    std::string bestSv = execute(filename.c_str());
    Address SvIp;
    NS_LOG_UNCOND(ip);
    uint16_t aux;
    //std::string bestSv="1.0.0.1 2.0.0.1 3.0.0.1";
    //system(filename.c_str());
    std::vector <std::string> BestServers;
    BestServers = split(bestSv.c_str(), " ");
    switch(BestServers[0].at(0))
    {
      case '1':
        SvIp=PAAddress;
        T1=Tf1;
        aux=0;
        break;
      case '2':
        SvIp=PEAddress;
        T2=Tf2;
        aux=1;
        break;
      case '3':
        SvIp=MGAddress;
        T3=Tf3;
        aux=2;
        break;
      case '4':
        SvIp=SPAddress;
        T4=Tf4;
        aux=3;
        break;
    }
    if ((ip!=bestSv and SClients[aux]+queue[aux]<MaxClientsSV))
    {
      std::cout << SvIp << "ServerId: \t" << i << " Cliente" << SClients[aux]<< std::endl;
      queue[aux]=queue[aux]+1;
      ServerHandover(clientApps, clientHelper, SvIp, clients,i);
    }
  }
  for (uint l = 0; l < 4; l++)
  {
    SBClients[l]=SClients[l];
  }
  Simulator::Schedule(Seconds(2),&politica2,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
}*/

static void
PingRtt (std::string context, Time rtt)
{
  std::vector <std::string> nodes;
  nodes = split(context.c_str(), "/");
  delays[std::stoi(nodes[2])-10].at(std::stoi(nodes[4]))=ToString(rtt);
  //std::cout << context << " " << ToString(rtt) << std::endl;
}

void
saveDelays(int32_t numberOfServers)
{
  std::string filename = "python3 src/Fog4MS/Delays.py " + dirTmp +" "+ToString(simulationId);
  for (int i = 0; i < numberOfServers; ++i)
  {
    for (int j = 0; j < numberOfServers; ++j)
    {
      filename= filename+" "+delays[i].at(j);
    }
  }
  system(filename.c_str());
  Simulator::Schedule(Seconds(1),&saveDelays,numberOfServers);
}

int
main (int argc, char *argv[])
{

  uint64_t segmentDuration = 40000;
  // The simulation id is used to distinguish log file results from potentially multiple consequent simulation runs.
  simulationId = 0;
  numberOfClients = 1;
  uint32_t numberOfServers = 10;
  std::string adaptationAlgo = "festive";
  std::string segmentSizeFilePath = "src/Fog4MS/dash/segmentSizesBigBuckVR.txt";
  seedValue = 0;
  uint16_t pol=4;

  //lastRx=[numberOfClients];

  CommandLine cmd;
  cmd.Usage ("Simulation of streaming with DASH.\n");
  cmd.AddValue ("simulationId", "The simulation's index (for logging purposes)", simulationId);
  cmd.AddValue ("numberOfClients", "The number of clients", numberOfClients);
  cmd.AddValue ("segmentDuration", "The duration of a video segment in microseconds", segmentDuration);
  cmd.AddValue ("adaptationAlgo", "The adaptation algorithm that the client uses for the simulation", adaptationAlgo);
  cmd.AddValue ("segmentSizeFile", "The relative path (from ns-3.x directory) to the file containing the segment sizes in bytes", segmentSizeFilePath);
  cmd.AddValue("seedValue", "random seed value.", seedValue);
  cmd.AddValue("politica", "value to choose the type of politica to be used (0 is AHP , 1 is Greedy, 2 is random and 3 is none. Default is 3)", pol);
  cmd.Parse (argc, argv);

  RngSeedManager::SetSeed(seedValue + 10000);
  srand(seedValue);
  rng.seed(seedValue);

  Config::SetDefault("ns3::TcpSocket::SegmentSize", UintegerValue (1446));
  Config::SetDefault("ns3::TcpSocket::SndBufSize", UintegerValue (524288));
  Config::SetDefault("ns3::TcpSocket::RcvBufSize", UintegerValue (524288));


  /* Create Nodes */
  NodeContainer networkNodes;
  networkNodes.Create (numberOfClients + numberOfServers+ numberOfServers);

  /* Determin access point and server node */
  Ptr<Node> PA = networkNodes.Get (0);
  Ptr<Node> PE = networkNodes.Get (1);
  Ptr<Node> GO = networkNodes.Get (2);
  Ptr<Node> MG = networkNodes.Get (3);
  Ptr<Node> DF = networkNodes.Get (4);
  Ptr<Node> BA = networkNodes.Get (5);
  Ptr<Node> RS = networkNodes.Get (6);
  Ptr<Node> SP = networkNodes.Get (7);
  Ptr<Node> RJ = networkNodes.Get (8);
  Ptr<Node> ES = networkNodes.Get (9);
  //Ptr<Node> apNode = networkNodes.Get (10);

  NodeContainer test;
  for (int i = 10; i < (2*numberOfServers); ++i)
  {
    test.Add (networkNodes.Get(i));
  }

  /* Configure clients as STAs in the WLAN */
  NodeContainer staContainer;
  /* Begin at +2, because position 0 is the access point and position 1 is the server */
  for (NodeContainer::Iterator i = networkNodes.Begin () + numberOfServers+ numberOfServers; i != networkNodes.End (); ++i)
    {
      staContainer.Add (*i);
    }

  /* Determin client nodes for object creation with client helper class */
  std::vector <std::pair <Ptr<Node>, std::string> > clients;
  for (NodeContainer::Iterator i = networkNodes.Begin () + numberOfServers+ numberOfServers; i != networkNodes.End (); ++i)
    {
      std::pair <Ptr<Node>, std::string> client (*i, adaptationAlgo);
      clients.push_back (client);
    }

  /* Set up WAN link between server node and access point*/
  NetDeviceContainer FibreNet;

  PointToPointHelper p2p;

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("10.5ms"));
  NetDeviceContainer PAPENet;
  PAPENet = p2p.Install (PA, PE);
  FibreNet.Add(PAPENet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("11ms"));
  NetDeviceContainer PAGONet;
  PAGONet = p2p.Install (PA,GO);
  FibreNet.Add(PAGONet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("13ms"));
  NetDeviceContainer PAMGNet;
  PAMGNet = p2p.Install (PA,MG);
  FibreNet.Add(PAMGNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("100Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("10.5ms"));
  NetDeviceContainer PEDFNet;
  PEDFNet = p2p.Install (PE,DF);
  FibreNet.Add(PEDFNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("5ms"));
  NetDeviceContainer PEBANet;
  PEBANet = p2p.Install (PE,BA);
  FibreNet.Add(PEBANet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("2.5ms"));
  NetDeviceContainer GODFNet;
  GODFNet = p2p.Install (GO,DF);
  FibreNet.Add(GODFNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("10ms"));
  NetDeviceContainer GORSNet;
  GORSNet = p2p.Install (GO,RS);
  FibreNet.Add(GORSNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("5ms"));
  NetDeviceContainer MGDFNet;
  MGDFNet = p2p.Install (MG,DF);
  FibreNet.Add(MGDFNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("4ms"));
  NetDeviceContainer MGSPNet;
  MGSPNet = p2p.Install (MG,SP);
  FibreNet.Add(MGSPNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("7ms"));
  NetDeviceContainer MGBANet;
  MGBANet = p2p.Install (MG,BA);
  FibreNet.Add(MGBANet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("6.5ms"));
  NetDeviceContainer DFRJNet;
  DFRJNet = p2p.Install (DF,RJ);
  FibreNet.Add(DFRJNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("6ms"));
  NetDeviceContainer BAESNet;
  BAESNet = p2p.Install (BA,ES);
  FibreNet.Add(BAESNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("6ms"));
  NetDeviceContainer RSSPNet;
  RSSPNet = p2p.Install (RS,SP);
  FibreNet.Add(RSSPNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("7ms"));
  NetDeviceContainer SPRJNet;
  SPRJNet = p2p.Install (SP,RJ);
  FibreNet.Add(SPRJNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("1000Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("7ms"));
  NetDeviceContainer RJESNet;
  RJESNet = p2p.Install (RJ,ES);
  FibreNet.Add(RJESNet);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("250Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer TestNet;
  for (int i = 0; i < numberOfServers; ++i)
  {
    TestNet.Add(p2p.Install (test.Get(i), networkNodes.Get(i)));
  }

  /* Internet stack */
  InternetStackHelper stack;
  stack.Install (networkNodes);
  //stack.Install (test);


  Ipv4AddressHelper address;
  address.SetBase ("1.0.0.0", "255.255.255.0");
  Ipv4InterfaceContainer FibreInterface;
  for (uint16_t u = 0; u < FibreNet.GetN(); u++)
    {
      FibreInterface.Add(address.Assign (FibreNet.Get(u)));
      address.NewNetwork();
    }
  //Ipv4InterfaceContainer wanInterface = address.Assign (PAPENet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface2 = address.Assign (PAGONet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface3 = address.Assign (PAMGNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface4 = address.Assign (PEDFNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface5 = address.Assign (PEBANet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface7 = address.Assign (GODFNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface8 = address.Assign (GORSNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface9 = address.Assign (MGDFNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface10 = address.Assign (MGSPNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface11 = address.Assign (MGBANet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface12 = address.Assign (DFRJNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface13 = address.Assign (BAESNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface14 = address.Assign (RSSPNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface15 = address.Assign (SPRJNet);
  //address.NewNetwork();
  //Ipv4InterfaceContainer wanInterface16 = address.Assign (RJESNet);


  /* Assign IP addresses */
  //Ipv4AddressHelper address;
  Ipv4AddressHelper address2;
  address2.SetBase ("2.0.0.0", "255.255.255.0");
  Ipv4InterfaceContainer testInterface;
  for (uint16_t u = 0; u < TestNet.GetN(); u++)
    {
      testInterface.Add(address2.Assign (TestNet.Get(u)));
      address2.NewNetwork();
    }

  //Ipv4AddressHelper address3;
  //Ipv4AddressHelper address4;
  //Ipv4AddressHelper address5;
  Ipv4AddressHelper address6;
  //Ipv4AddressHelper address7;

  /* IPs for WAN */
    //address.SetBase ("1.0.0.0", "255.255.255.0");
    //address2.SetBase ("2.0.0.0", "255.255.255.0");
    //address3.SetBase ("3.0.0.0", "255.255.255.0");
    //address4.SetBase ("4.0.0.0", "255.255.255.0");
    //address5.SetBase ("5.0.0.0", "255.255.255.0");
    //address7.SetBase ("7.0.0.0", "255.255.255.0");
    //Ipv4InterfaceContainer wanInterface = address.Assign (wanIpDevices);
    //Ipv4InterfaceContainer wanInterface2 = address2.Assign (wanIpDevices2);
    //Ipv4InterfaceContainer wanInterface3 = address3.Assign (wanIpDevices3);
    //Ipv4InterfaceContainer wanInterface4 = address4.Assign (wanIpDevices4);
    //Ipv4InterfaceContainer wanInterface5 = address5.Assign (wanIpDevicesHops);
    //Ipv4InterfaceContainer wanInterface7 = address7.Assign (wanIpDevicesHops1);


for (uint16_t u = 0; u < 20; u++)
{
  Ptr < Node > node = networkNodes.Get(u);
  Ptr < Ipv4 > ipv4 = node->GetObject < Ipv4 > ();
  //Ptr < Address > addr = node->GetObject < Address > ();
  Ipv4InterfaceAddress iaddr = ipv4->GetAddress(1, 0);
  Ipv4Address addri = iaddr.GetLocal();
  NS_LOG_UNCOND(addri);
  if (u<10)
    pingAddress.push_back(addri);
  else 
    fogAddress.push_back(addri);
}   

//server1Address = fogAddress[0];
//server2Address= fogAddress[1];
//server3Address= fogAddress[2];
//cloudAddress= fogAddress[3];
//NS_LOG_UNCOND(wanInterface.GetAddress (0));
//NS_LOG_UNCOND(wanInterface.GetAddress (1));
//NS_LOG_UNCOND(wanInterface9.GetAddress (0));
//NS_LOG_UNCOND(wanInterface10.GetAddress (1));
//PAAddress = Address(wanInterface.GetAddress (0));
//PEAddress = Address(wanInterface4.GetAddress (0));
//MGAddress = Address(wanInterface9.GetAddress (0));
//SPAddress = Address(wanInterface15.GetAddress (0));

PAAddress = fogAddress[0];
PEAddress = fogAddress[1];
MGAddress = fogAddress[3];
SPAddress = fogAddress[7];
  
  address6.SetBase ("192.168.0.0", "255.255.255.0");
  p2p.SetDeviceAttribute ("DataRate", StringValue ("100Mb/s")); // This must not be more than the maximum throughput in 802.11n
  p2p.SetDeviceAttribute ("Mtu", UintegerValue (1500));
  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer ClientsNet;
  //for (uint16_t u = 0; u < numberOfClients; u++)
  //{
  //  address6.NewNetwork();
  //  NetDeviceContainer ClientsNet = p2p.Install (apNode,networkNodes.Get (9+u));
  //  Ipv4InterfaceContainer wanInterface6 = address6.Assign (ClientsNet);;
  //}


  // create folder so we can log the positions of the clients
  const char * mylogsDir = dashLogDirectory.c_str();
  mkdir (mylogsDir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  std::string tobascoDirTmp = dashLogDirectory + adaptationAlgo + "/";
  const char * tobascoDir = tobascoDirTmp.c_str();
  //const char * tobascoDir = (ToString (dashLogDirectory) + ToString (adaptationAlgo) + "/").c_str();
  mkdir (tobascoDir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  dirTmp = dashLogDirectory + adaptationAlgo + "/" + ToString (numberOfClients) + "/";
  //const char * dir = (ToString (dashLogDirectory) + ToString (adaptationAlgo) + "/" + ToString (numberOfClients) + "/").c_str();
  const char * dir = dirTmp.c_str();
  mkdir(dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  dirTmp = dashLogDirectory + adaptationAlgo + "/" + ToString (numberOfClients) + "/" + ToString (pol) + "/";
  //const char * dir = (ToString (dashLogDirectory) + ToString (adaptationAlgo) + "/" + ToString (numberOfClients) + "/").c_str();
  dir = dirTmp.c_str();
  mkdir(dir, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);

  std::cout << mylogsDir << "\n";
  std::cout << tobascoDir << "\n";
  std::cout << dir << "\n";

  MobilityHelper mobility;
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (networkNodes);

  // if logging of the packets between AP---Server or AP and the STAs is wanted, these two lines can be activated

  // p2p.EnablePcapAll ("p2p-", true);
  // wifiPhy.EnablePcapAll ("wifi-", true);
  ApplicationContainer apps;
  for (int i = 0; i < test.GetN(); ++i)
  {
    V4PingHelper ping = V4PingHelper (pingAddress[i]);
    for (int j = 0; j < test.GetN(); ++j)
    {
      apps.Add(ping.Install (test.Get(j)));
    }
  }
  apps.Start (Seconds (2.0));
    //V4PingHelper ping = V4PingHelper (fogAddress[0]);
    //ApplicationContainer apps = ping.Install (test.Get(0));
    //V4PingHelper ping2 = V4PingHelper (fogAddress[1]);
    //apps.Add(ping2.Install (test.Get(0)));
    //V4PingHelper ping3 = V4PingHelper (fogAddress[2]);
    //apps.Add(ping3.Install (test.Get(0)));
    //V4PingHelper ping4 = V4PingHelper (fogAddress[3]);
    //apps.Add(ping4.Install (test.Get(0)));
    //V4PingHelper ping5 = V4PingHelper (fogAddress[4]);
    //apps.Add(ping5.Install (test.Get(0)));

  // finally, print the ping rtts.
  Config::Connect ("/NodeList/*/ApplicationList/*/$ns3::V4Ping/Rtt",MakeCallback (&PingRtt));

  //Packet::EnablePrinting ();

  uint16_t port = 9;

  NodeContainer servers;
  for (NodeContainer::Iterator i = networkNodes.Begin ()+numberOfServers; i != networkNodes.Begin ()+numberOfServers+numberOfServers; ++i)
  {
    servers.Add (*i);
  }
  //servers.Add(PA);
  //servers.Add(PE);
  //servers.Add(MG);
  //servers.Add(SP);
  Controller (numberOfServers, simulationId, dirTmp);
  std::vector<uint16_t> content;
  ApplicationContainer serverApp;
  //NS_LOG_UNCOND(serverData.memorySize.at(0));
  TcpStreamServerHelper serverHelper (port,simulationId,dirTmp); //NS_LOG_UNCOND("dash Install 277");
  for (uint16_t u = 0; u < servers.GetN(); u++)
  {
    serverHelper.SetAttribute ("RemoteAddress", AddressValue (fogAddress[u]));
    serverHelper.SetAttribute ("ServerId", UintegerValue (u));
    serverApp = serverHelper.Install (servers.Get(u));
    if (u<=1 or u==5 or u==9)
    {
      serverInitialise (u,16000,16000, content, fogAddress[u],0.000085);
    }
    else
    {
      if (u==7)
      {
        serverInitialise (u,64000,64000, content, fogAddress[u],0.00034);
      }
      else
      {
        serverInitialise (u,32000,32000, content, fogAddress[u],0.00017);
      }
    }
    
    printInformation (u);
  }
  //ApplicationContainer serverApp = serverHelper.Install (PA);//NS_LOG_UNCOND("dash Install 278");
  //serverHelper.SetAttribute ("RemoteAddress", AddressValue (PEAddress));
  //serverApp = serverHelper.Install (PE);
  //serverHelper.SetAttribute ("RemoteAddress", AddressValue (MGAddress));
  //serverApp = serverHelper.Install (MG);
  //serverHelper.SetAttribute ("RemoteAddress", AddressValue (SPAddress));
  //serverApp = serverHelper.Install (SP);
  serverApp.Start (Seconds (1.0));
  //serverApp2.Start (Seconds (1.0));
  //serverApp3.Start (Seconds (1.0));
  //std::vector <std::pair <Ptr<Node>, std::string> > clients_temp0;
  //std::vector <std::pair <Ptr<Node>, std::string> > clients_temp1;
  //std::vector <std::pair <Ptr<Node>, std::string> > clients_temp2;
  //std::vector <std::pair <Ptr<Node>, std::string> > clients_temp3;
  /*
  for (uint i = 0; i < numberOfClients; i++)
    {
      if(i<(numberOfClients+(4-(numberOfClients % 4)))/4)
      {
        clients_temp0.push_back(clients[i]);
      }
      else 
        if(i<2*(numberOfClients+(4-(numberOfClients % 4)))/4)
          {
            clients_temp1.push_back(clients[i]);
          }
        else
          if(i<3*(numberOfClients+(4-(numberOfClients % 4)))/4)
          {
            clients_temp2.push_back(clients[i]);
          }
          else
          {
            clients_temp3.push_back(clients[i]);
          }
    }
  
  /* Install TCP/UDP Transmitter on the station */
  InitializeLogFiles (dashLogDirectory, adaptationAlgo,ToString(numberOfClients),ToString(simulationId),ToString(pol));

  TcpStreamClientHelper clientHelper (SPAddress, port,pol);
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("NumberOfClients", UintegerValue(numberOfClients));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  //clientHelper.SetAttribute ("RemoteAddress", AddressValue (PAAddress));
  ApplicationContainer clientApps ;//= clientHelper.Install (clients_temp0);
  for (uint i = 0; i < numberOfClients; i++)
  {
    int cont = zipf(0.7,100);
    int quali= zipfQuality(0.7,7);
    quali=qualis[quali];
    //segmentSizeFilePath = "src/Fog4MS/dash/segmentSizesBigBuck"+ToString(quali)+".txt";
    uint32_t value = uniformDis();
    NetDeviceContainer ClientsNet = p2p.Install (networkNodes.Get(value),staContainer.Get (i));
    Ipv4InterfaceContainer wanInterface6 = address6.Assign (ClientsNet);
    address6.NewNetwork();
    std::vector <std::pair <Ptr<Node>, std::string> > clients_temp0;
    clients_temp0.push_back(clients.at(i));
    clientHelper.SetAttribute ("ServerId", UintegerValue (value));
    clientHelper.SetAttribute ("ContentId", UintegerValue (cont));
    clientHelper.SetAttribute ("ContentSize", DoubleValue (sizes[quali]));
    clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
    //clientHelper.SetAttribute ("RemoteAddress", AddressValue (choiceServer(5,2000)));
    clientApps.Add(clientHelper.Install (clients_temp0,i));
    Ptr<Application> app=clientApps.Get(i);
    double t=poisson();
    app->SetStartTime (Seconds(t));
    LogClient(i,value,cont,quali,sizes[quali],t);
  }
/*
  //TcpStreamClientHelper clientHelper2 (server2Address, port);
  clientHelper.SetAttribute ("RemoteAddress", AddressValue (server2Address));
  clientHelper.SetAttribute ("RemotePort", UintegerValue (port));
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("NumberOfClients", UintegerValue(numberOfClients));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (1));
  clientApps.Add(clientHelper.Install (clients_temp1));

  //TcpStreamClientHelper clientHelper3 (server3Address, port);
  clientHelper.SetAttribute ("RemoteAddress", AddressValue (server3Address));
  clientHelper.SetAttribute ("RemotePort", UintegerValue (port));
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("NumberOfClients", UintegerValue(numberOfClients));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (2));
  clientApps.Add(clientHelper.Install (clients_temp2));

  clientHelper.SetAttribute ("RemoteAddress", AddressValue (cloudAddress));
  clientHelper.SetAttribute ("RemotePort", UintegerValue (port));
  clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper.SetAttribute ("NumberOfClients", UintegerValue(numberOfClients));
  clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId));
  clientHelper.SetAttribute ("ServerId", UintegerValue (3));
  clientApps.Add(clientHelper.Install (clients));
/*  
  for (uint i = 0; i < clientApps.GetN (); i++)
    {
      double startTime = 2.0;
      clientApps.Get (i)->SetStartTime (Seconds (startTime));
    }
*//*
  for (uint i = 0; i < staContainer.GetN (); i++)
    {
      Ptr<Application> app = staContainer.Get (i)->GetApplication(0);
      double startTime = 2.0 ;
      app->SetStartTime (Seconds (startTime));
      //app->SetStopTime(Seconds (startTime+10));
    }*/
  throughputs.reserve(numberOfClients);
  throughputs.resize(numberOfClients);
  Stalls.reserve(numberOfClients);
  Stalls.resize(numberOfClients);
  Rebuffers.reserve(numberOfClients);
  Rebuffers.resize(numberOfClients);

  /* Populate routing table */

  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();
  Ipv4GlobalRoutingHelper g;
  Ptr<OutputStreamWrapper> routingStream = Create<OutputStreamWrapper> 
  ("dynamic-global-routing.routes", std::ios::out);
  g.PrintRoutingTableAllAt (Seconds (5), routingStream);
  //teste.memorySize.reserve (numberOfClients);
  //teste.memorySize.resize (numberOfClients);
  //NS_LOG_UNCOND(teste.memorySize.size());
/*

  /* Install TCP Receiver on the access point */
/*
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp0;
  clients_temp0.push_back(clients[0]);*/

  /* Install TCP/UDP Transmitter on the station */
  //TcpStreamClientHelper clientHelper (serverAddress, port); //NS_LOG_UNCOND("dash Install 288");
  //clientHelper.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  //clientHelper.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  //clientHelper.SetAttribute ("NumberOfClients", UintegerValue(numberOfClients));
  //clientHelper.SetAttribute ("SimulationId", UintegerValue (simulationId)); //NS_LOG_UNCOND("dash Install 292");
  //ApplicationContainer clientApps = clientHelper.Install (clients); //NS_LOG_UNCOND("dash Install 293");


/*
  std::vector <std::pair <Ptr<Node>, std::string> > clients_temp1;
  clients_temp1.push_back(clients[1]);

  TcpStreamClientHelper clientHelper2 (serverAddress2, port);
  clientHelper2.SetAttribute ("SegmentDuration", UintegerValue (segmentDuration));
  clientHelper2.SetAttribute ("SegmentSizeFilePath", StringValue (segmentSizeFilePath));
  clientHelper2.SetAttribute ("NumberOfClients", UintegerValue(numberOfClients));
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
    //Simulator::Schedule(Seconds(20.001),&politica,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
  }
  else
  {
    if (pol==1)
    {
      type="guloso";
      //Simulator::Schedule(Seconds(5.001),&politica2,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
    }
    else
    {
      if (pol==2)
      {
      type="aleatorio";
      //Simulator::Schedule(Seconds(5.001),&politica2,clientApps,clientHelper,clients,serverApp, serverHelper,servers);
      }
    }
  }
  
  Simulator::Stop(Seconds(180));
  NS_LOG_INFO ("Run Simulation.");
  NS_LOG_INFO ("Sim: " << simulationId << "Clients: " << numberOfClients);
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
  Simulator::Schedule(Seconds(3.5),&saveDelays,numberOfServers);
  Simulator::Schedule(Seconds(3),&getStall,clientApps,clientHelper,clients);
  //Simulator::Schedule(Seconds(5),&stopSim,clientHelper,staContainer);
  Simulator::Schedule(Seconds(10),&getStartTime,clientApps,clientHelper,clients);
  //Simulator::Schedule(Seconds(1),&throughput,flowMonitor,classifier);
  Simulator::Run ();
  //flowMonitor->SerializeToXmlFile ("results.xml" , true, true );
  Simulator::Destroy ();
  NS_LOG_INFO ("Done.");

}
