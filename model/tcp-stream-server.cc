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

#include "ns3/log.h"
#include "ns3/ipv4-address.h"
#include "ns3/ipv6-address.h"
#include "ns3/address-utils.h"
#include "ns3/nstime.h"
#include "ns3/inet-socket-address.h"
#include "ns3/inet6-socket-address.h"
#include "ns3/socket.h"
#include "ns3/tcp-socket.h"
#include "ns3/simulator.h"
#include "ns3/socket-factory.h"
#include "ns3/packet.h"
#include "ns3/uinteger.h"
#include "ns3/tcp-socket-factory.h"
#include "tcp-stream-server.h"
#include "ns3/global-value.h"
#include <ns3/core-module.h>
#include "tcp-stream-client.h"
#include "ns3/trace-source-accessor.h"
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include "tcp-stream-controller.h"

namespace ns3 {

template <typename T>
std::string ToString (T val)
{
  std::stringstream stream;
  stream << val;
  return stream.str ();
}


NS_LOG_COMPONENT_DEFINE ("TcpStreamServerApplication");

NS_OBJECT_ENSURE_REGISTERED (TcpStreamServer);

TypeId
TcpStreamServer::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::TcpStreamServer")
    .SetParent<Application> ()
    .SetGroupName ("Applications")
    .AddConstructor<TcpStreamServer> ()
    .AddAttribute ("RemoteAddress",
                   "The destination Address of the outbound packets",
                   AddressValue (),
                   MakeAddressAccessor (&TcpStreamServer::serverIp),
                   MakeAddressChecker ())
    .AddAttribute ("Port", "Port on which we listen for incoming packets.",
                   UintegerValue (9),
                   MakeUintegerAccessor (&TcpStreamServer::m_port),
                   MakeUintegerChecker<uint16_t> ())
    .AddAttribute ("directory",
                   "The relative path (from ns-3.x directory) to the dash-log-files",
                   StringValue ("bitrates.txt"),
                   MakeStringAccessor (&TcpStreamServer::directory),
                   MakeStringChecker ())
    .AddAttribute ("SimulationId",
                   "The ID of the current simulation, for logging purposes",
                   UintegerValue (0),
                   MakeUintegerAccessor (&TcpStreamServer::simulationId),
                   MakeUintegerChecker<uint32_t> ())
    .AddAttribute ("ServerId",
                   "The ID of the initial server for the client object, for logging purposes",
                   UintegerValue (0),
                   MakeUintegerAccessor (&TcpStreamServer::serverId),
                   MakeUintegerChecker<uint32_t> ())
  ;
  return tid;
}

TcpStreamServer::TcpStreamServer ()
{
  NS_LOG_FUNCTION (this);
  totalBytesSend = 0;
  MME = 0;
  n=3;
}

TcpStreamServer::~TcpStreamServer ()
{ //NS_LOG_UNCOND("nao eh aqui no server");
  NS_LOG_FUNCTION (this);
  m_socket = 0;
  m_socket6 = 0;
}

void
TcpStreamServer::DoDispose (void)
{
  NS_LOG_FUNCTION (this);
  Application::DoDispose ();
}

void
TcpStreamServer::StartApplication (void)
{
  NS_LOG_FUNCTION (this); //NS_LOG_UNCOND("server StartApplication 82");
  //std::vector <uint16_t> t;
  //serverUpdate(0,8192.0,8192.0,t,serverIp);
  //serverData.memorySize.at(0)=6128.0;
  if (m_socket == 0)
    {
      TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
      m_socket = Socket::CreateSocket (GetNode (), tid);
      InetSocketAddress local = InetSocketAddress (Ipv4Address::GetAny (), m_port);
      m_socket->Bind (local);
      m_socket->Listen ();
    }

  if (m_socket6 == 0)
    {
      TypeId tid = TypeId::LookupByName ("ns3::TcpSocketFactory");
      m_socket6 = Socket::CreateSocket (GetNode (), tid);
      Inet6SocketAddress local6 = Inet6SocketAddress (Ipv6Address::GetAny (), m_port);
      m_socket6->Bind (local6);
      m_socket->Listen ();
    }
  

  // Accept connection requests from remote hosts.
  m_socket->SetAcceptCallback (MakeNullCallback<bool, Ptr< Socket >, const Address &> (),
                               MakeCallback (&TcpStreamServer::HandleAccept,this));
  m_socket->SetCloseCallbacks (
    MakeCallback (&TcpStreamServer::HandlePeerClose, this),
    MakeCallback (&TcpStreamServer::HandlePeerError, this));
  InitializeLogFiles (GetServerAddress());
}

void
TcpStreamServer::StopApplication ()
{
  NS_LOG_FUNCTION (this); //NS_LOG_UNCOND("server StopApplication 113");

  if (m_socket != 0)
    {
      m_socket->Close ();
      m_socket->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
    }
  if (m_socket6 != 0)
    {
      m_socket6->Close ();
      m_socket6->SetRecvCallback (MakeNullCallback<void, Ptr<Socket> > ());
    }
}

void
TcpStreamServer::HandleRead (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
  Ptr<Packet> packet;
  //std::cout << Simulator::Now ().GetSeconds () << "s: \t" << " read" << std::endl;
  Address from;
  packet = socket->RecvFrom (from);
  int64_t packetSizeToReturn = GetCommand (packet);
  // these values will be accessible by the clients Address from.
  m_callbackData [from].currentTxBytes = 0;
  m_callbackData [from].packetSizeToReturn = packetSizeToReturn;
  m_callbackData [from].send = true;
  HandleSend (socket, socket->GetTxAvailable ());
}

void
TcpStreamServer::HandleSend (Ptr<Socket> socket, uint32_t txSpace)
{
  Address from;
  socket->GetPeerName (from);
  // look up values for the connected client and whose values are stored in from
  if (m_callbackData [from].currentTxBytes == m_callbackData [from].packetSizeToReturn)
    {
      m_callbackData [from].currentTxBytes = 0;
      m_callbackData [from].packetSizeToReturn = 0;
      m_callbackData [from].send = false;
      return;
    }
  if (socket->GetTxAvailable () > 0 && m_callbackData [from].send)
    {
      int32_t toSend;
      toSend = std::min (socket->GetTxAvailable (), m_callbackData [from].packetSizeToReturn - m_callbackData [from].currentTxBytes);
      Ptr<Packet> packet = Create<Packet> (toSend);
      int amountSent = socket->Send (packet, 0);
      totalBytesSend+=amountSent;
      //NS_LOG_UNCOND("aqui");NS_LOG_UNCOND(amountSent);
      if (amountSent > 0)
        {
          m_callbackData [from].currentTxBytes += amountSent;
        }
      // We exit this part, when no bytes have been sent, as the send side buffer is full.
      // The "HandleSend" callback will fire when some buffer space has freed up.
      else
        {
          return;
        }
    }
}

void
TcpStreamServer::HandleAccept (Ptr<Socket> s, const Address& from)
{
  NS_LOG_FUNCTION (this << s << from);
  callbackData cbd;
  cbd.currentTxBytes = 0;
  cbd.packetSizeToReturn = 0;
  cbd.send = false;
  m_callbackData [from] = cbd;
  m_connectedClients.push_back (from);
  setOn(serverId);
  s->SetRecvCallback (MakeCallback (&TcpStreamServer::HandleRead, this));
  s->SetSendCallback ( MakeCallback (&TcpStreamServer::HandleSend, this));
}

void
TcpStreamServer::HandlePeerClose (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
  Address from;
  socket->GetPeerName (from);
  for (std::vector<Address>::iterator it = m_connectedClients.begin (); it != m_connectedClients.end (); ++it)
    {
      if (*it == from)
        {
          m_connectedClients.erase (it);
          // No more clients left in m_connectedClients, simulation is done.
          if (m_connectedClients.size () == 0)
            {
              setOff(serverId);
              //Simulator::Stop ();
            }
          return;
        }
    }
}

void
TcpStreamServer::HandlePeerError (Ptr<Socket> socket)
{
  NS_LOG_FUNCTION (this << socket);
}

int64_t
TcpStreamServer::GetCommand (Ptr<Packet> packet)
{
  int64_t packetSizeToReturn;
  uint8_t *buffer = new uint8_t [packet->GetSize ()];
  packet->CopyData (buffer, packet->GetSize ());
  std::stringstream ss;
  ss << buffer;
  std::string str;
  ss >> str;
  std::stringstream convert (str);
  convert >> packetSizeToReturn;
  return packetSizeToReturn;
}

double
TcpStreamServer::serverThroughput ()
{
  Time now = Simulator::Now ();
  double Throughput = totalBytesSend * (double) 8 / 1e6;
  //std::cout << now.GetSeconds () << "s: \t" << Throughput << " Mbit/s" << std::endl;
  MME = MME + (2*(Throughput-MME)/(n+1));
  //std::cout << "MME: \t" << MME << " Mbit/s" << std::endl;
  totalBytesSend=0;
  LogThroughput (Throughput, MME);
  return Throughput;
}

std::string
TcpStreamServer::GetServerAddress()
{
  std::string a = ToString(Ipv4Address::ConvertFrom (serverIp));
  return a;
}

uint32_t
TcpStreamServer::GetNumberOfClients()
{
  uint32_t a = m_connectedClients.size ();
  return a;
}

void
TcpStreamServer::LogThroughput (double packetSize, double MME)
{
  NS_LOG_FUNCTION (this);
  std::ostringstream vts;
  if(!serverData.allocatedContentType.at(serverId).empty())
  {
    std::copy(serverData.allocatedContentType.at(serverId).begin(), serverData.allocatedContentType.at(serverId).end()-1,std::ostream_iterator<int>(vts, "/"));
    vts << serverData.allocatedContentType.at(serverId).back();
  }
  throughputLog << std::setfill (' ') << std::setw (0) << Simulator::Now ().GetMicroSeconds ()  / (double) 1000000 << ";"
                << std::setfill (' ') << std::setw (0) << serverData.onOff.at(serverId) << ";"
                << std::setfill (' ') << std::setw (0) << serverData.cost.at(serverId) << ";"
                << std::setfill (' ') << std::setw (0) << packetSize << ";"
                << std::setfill (' ') << std::setw (0) << MME << ";"
                << std::setfill (' ') << std::setw (0) << serverData.memorySize.at(serverId) << ";"
                << std::setfill (' ') << std::setw (0) << serverData.memoryFree.at(serverId) << ";"
                << std::setfill (' ') << std::setw (0) << GetServerAddress() << ";"
                << std::setfill (' ') << std::setw (0) << vts.str() << ";\n";
  throughputLog.flush ();
}

void  
TcpStreamServer::InitializeLogFiles (std::string server)
{
  NS_LOG_FUNCTION (this);

  std::string tLog = directory + "throughputServer"+ "_sim" + ToString(simulationId) +"_" + server + "_" +"Log.csv";
  throughputLog.open (tLog.c_str ());
  throughputLog << "Time_Now;OnOff;Cost;MBytes_Received;MME;TotalMemory;FreeMemory;ServerAddress;AllocatedContent\n";
  throughputLog.flush ();
}

} // Namespace ns3
