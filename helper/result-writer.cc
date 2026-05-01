#include "result-writer.h"
#include "wsn-network-helper.h"
#include "ns3/log.h"
#include "ns3/mobility-model.h"
#include <fstream>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <sys/stat.h>
#include <sys/types.h>

NS_LOG_COMPONENT_DEFINE("ResultWriter");

namespace ns3 {
namespace wsn {
namespace uav {

ResultWriter::ResultWriter(const std::string& outputDir)
    : m_outputDir(outputDir) {}

bool ResultWriter::Initialize() const {
    // Create directory recursively
    std::string cmd = "mkdir -p " + m_outputDir;
    int ret = system(cmd.c_str());
    return ret == 0;
}

std::string ResultWriter::GetPath(const std::string& filename) const {
    return m_outputDir + "/" + filename;
}

void ResultWriter::WriteMetrics(const SimulationResults& results, const SimulationConfig& config) const {
    std::ofstream out(GetPath("metrics.csv"));
    if (!out.is_open()) {
        NS_LOG_ERROR("Failed to open metrics.csv");
        return;
    }
    
    out << "metric,value\n";
    out << "detected," << (results.detected ? "true" : "false") << "\n";
    out << "detection_time_seconds," << results.detectionTime << "\n";
    out << "detection_node_id," << results.detectionNodeId << "\n";
    out << "uav_path_length_meters," << results.uavPathLength << "\n";
    out << "cooperation_gain," << results.cooperationGain << "\n";
    out << "total_nodes," << results.totalNodes << "\n";
    out << "candidate_nodes," << results.candidateNodes << "\n";
    out << "total_fragments_delivered," << results.totalFragmentsDelivered << "\n";
    out << "fragments_from_uav," << results.fragmentsFromUav << "\n";
    out << "\n[CONFIG]\n";
    out << "grid_size," << config.gridSize << "\n";
    out << "num_fragments," << config.numFragments << "\n";
    out << "num_uavs," << 1 << "\n";
    out << "uav_altitude_m," << config.uavAltitude << "\n";
    out << "uav_speed_mps," << config.uavSpeed << "\n";
    out << "broadcast_interval_s," << config.broadcastInterval << "\n";
    out << "seed," << config.seed << "\n";
    out << "run_id," << config.runId << "\n";
    
    out.close();
    NS_LOG_INFO("Metrics written to " << GetPath("metrics.csv"));
}

void ResultWriter::WriteTrajectories(Ptr<StatisticsCollector> collector) const {
    if (!collector) return;
    
    std::ofstream out(GetPath("trajectories.csv"));
    if (!out.is_open()) {
        NS_LOG_ERROR("Failed to open trajectories.csv");
        return;
    }
    
    out << "time_seconds,x_meters,y_meters,z_meters\n";
    
    const auto& positions = collector->GetUavPositions();
    for (const auto& record : positions) {
        out << record.timeSeconds << ","
            << record.x << ","
            << record.y << ","
            << record.z << "\n";
    }
    
    out.close();
    NS_LOG_INFO("Trajectories written to " << GetPath("trajectories.csv"));
}

void ResultWriter::WritePackets(Ptr<StatisticsCollector> collector, const NodeContainer& groundNodes) const {
    if (!collector) return;

    // Finalize packet records: mark unmatched broadcasts as dropped (0.1s contact window)
    collector->FinalizePacketRecords(0.1);

    std::ofstream out(GetPath("packets.csv"));
    if (!out.is_open()) {
        NS_LOG_ERROR("Failed to open packets.csv");
        return;
    }

    out << "time_seconds,src_node_id,dst_node_id,fragment_id,success,rssi_dbm\n";

    auto packets = collector->GetPacketRecords();

    // Output only UAV packets (srcNodeId >= groundNodes.GetN())
    // This matches the visualization filter for consistency
    for (const auto& record : packets) {
        if (record.srcNodeId < groundNodes.GetN()) {
            continue;  // Skip ground node packets
        }

        out << record.timeSeconds << ","
            << record.srcNodeId << ","
            << record.dstNodeId << ","
            << record.fragmentId << ","
            << (record.success ? "true" : "false") << ","
            << record.rssiDbm << "\n";
    }

    out.close();
    NS_LOG_INFO("Packets written to " << GetPath("packets.csv"));
}

void ResultWriter::WriteConfig(const SimulationConfig& config) const {
    std::ofstream out(GetPath("config.txt"));
    if (!out.is_open()) {
        NS_LOG_ERROR("Failed to open config.txt");
        return;
    }
    
    out << "Simulation Configuration\n";
    out << "=======================\n";
    out << "Grid size: " << config.gridSize << "x" << config.gridSize << "\n";
    out << "Grid spacing: " << config.gridSpacing << " meters\n";
    out << "Total nodes: " << (config.gridSize * config.gridSize) << "\n";
    out << "Num fragments: " << config.numFragments << "\n";
    out << "UAV altitude: " << config.uavAltitude << " meters\n";
    out << "UAV speed: " << config.uavSpeed << " m/s\n";
    out << "Broadcast interval: " << config.broadcastInterval << " seconds\n";
    out << "Cooperation threshold: " << config.cooperationThreshold << "\n";
    out << "Alert threshold: " << config.alertThreshold << "\n";
    out << "Suspicious fraction: " << config.suspiciousPercent << "\n";
    out << "Simulation time: " << config.simTime << " seconds\n";
    out << "Seed: " << config.seed << "\n";
    out << "Run ID: " << config.runId << "\n";
    out << "Output dir: " << config.outputDir << "\n";
    out << "Use perfect channel: " << (config.usePerfectChannel ? "yes" : "no") << "\n";
    out << "Use GMC: " << (config.useGmc ? "yes" : "no") << "\n";
    
    out.close();
    NS_LOG_INFO("Config written to " << GetPath("config.txt"));
}

void ResultWriter::WriteVisualizationData(const SimulationResults& results,
                                          const SimulationConfig& config,
                                          const NodeContainer& groundNodes,
                                          Ptr<StatisticsCollector> collector,
                                          const std::set<uint32_t>& candidateNodes) const {
    // Generate timestamp for unique identification
    auto now = std::time(nullptr);
    auto tm = *std::localtime(&now);
    std::ostringstream oss_time;
    oss_time << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
    std::string timestamp = oss_time.str();

    // Build JSON data string
    std::ostringstream data_json;
    data_json << "{\n";
    data_json << "  \"timestamp\": \"" << timestamp << "\",\n";
    data_json << "  \"config\": {\n";
    data_json << "    \"gridSize\": " << config.gridSize << ",\n";
    data_json << "    \"gridSpacing\": " << config.gridSpacing << ",\n";
    data_json << "    \"numNodes\": " << config.gridSize * config.gridSize << ",\n";
    data_json << "    \"numFragments\": " << config.numFragments << ",\n";
    data_json << "    \"simTime\": " << config.simTime << ",\n";
    data_json << "    \"detectionTime\": " << results.detectionTime << ",\n";
    data_json << "    \"detected\": " << (results.detected ? "true" : "false") << ",\n";
    data_json << "    \"uavPathLength\": " << std::fixed << std::setprecision(2) << results.uavPathLength << ",\n";
    data_json << "    \"cooperationGain\": " << std::setprecision(4) << results.cooperationGain << "\n";
    data_json << "  },\n";

    // Build nodes as object keyed by node ID (not array, to handle sparse IDs)
    data_json << "  \"nodes\": {\n";
    bool firstNode = true;

    // Add ground nodes (fragment counts will be calculated dynamically during playback)
    for (uint32_t i = 0; i < groundNodes.GetN(); i++) {
        auto mob = groundNodes.Get(i)->GetObject<MobilityModel>();
        Vector pos = mob->GetPosition();
        bool isCandidate = candidateNodes.count(i) > 0;
        bool isDetectionNode = (i == results.detectionNodeId);

        if (!firstNode) {
            data_json << ",\n";
        }
        data_json << "    \"" << i << "\": {\"id\": " << i << ", \"x\": " << std::fixed << std::setprecision(1) << pos.x
                  << ", \"y\": " << pos.y << ", \"z\": " << pos.z
                  << ", \"isCandidate\": " << (isCandidate ? "true" : "false")
                  << ", \"isDetectionNode\": " << (isDetectionNode ? "true" : "false") << "}";
        firstNode = false;
    }

    // Add UAV node (node ID = groundNodes.GetN() + 1, to match wsn-network-helper line 215)
    Vector uavPos(0, 0, config.uavAltitude);
    if (collector && !collector->GetUavPositions().empty()) {
        const auto& firstPos = collector->GetUavPositions()[0];
        uavPos = Vector(firstPos.x, firstPos.y, firstPos.z);
    }
    uint32_t uavNodeId = groundNodes.GetN() + 1;
    if (!firstNode) {
        data_json << ",\n";
    }
    data_json << "    \"" << uavNodeId << "\": {\"id\": " << uavNodeId
              << ", \"x\": " << std::fixed << std::setprecision(1) << uavPos.x
              << ", \"y\": " << uavPos.y << ", \"z\": " << uavPos.z
              << ", \"isCandidate\": false, \"isDetectionNode\": false}\n";

    data_json << "  },\n";

    data_json << "  \"uavTrajectory\": [\n";
    if (collector) {
        const auto& positions = collector->GetUavPositions();
        for (size_t i = 0; i < positions.size(); i++) {
            const auto& record = positions[i];
            data_json << "    {\"t\": " << std::fixed << std::setprecision(2) << record.timeSeconds
                      << ", \"x\": " << std::setprecision(1) << record.x
                      << ", \"y\": " << record.y
                      << ", \"z\": " << record.z << "}";
            if (i < positions.size() - 1) {
                data_json << ",\n";
            } else {
                data_json << "\n";
            }
        }
    }
    data_json << "  ],\n";

    data_json << "  \"packets\": [\n";
    if (collector) {
        const auto& packets = collector->GetPacketRecords();
        bool firstPacket = true;
        for (size_t i = 0; i < packets.size(); i++) {
            const auto& pkt = packets[i];

            // Determine packet type: UAV (src >= groundNodes.GetN()) or G2G (src < groundNodes.GetN())
            bool isUav = (pkt.srcNodeId >= groundNodes.GetN());

            // Skip G2G (ground-to-ground) cooperation packets
            if (!isUav) {
                continue;
            }

            // Skip broadcast packets (dst = 0xFFFFFFFF)
            if (pkt.dstNodeId == 0xFFFFFFFF) {
                continue;
            }

            // Skip invalid packets
            if (pkt.dstNodeId >= groundNodes.GetN()) {
                // Invalid destination
                continue;
            }

            if (!firstPacket) {
                data_json << ",\n";
            }

            // Add packet type: "uav" or "g2g"
            data_json << "    {\"t\": " << std::fixed << std::setprecision(2) << pkt.timeSeconds
                      << ", \"type\": \"" << (isUav ? "uav" : "g2g") << "\""
                      << ", \"src\": " << pkt.srcNodeId
                      << ", \"dst\": " << pkt.dstNodeId
                      << ", \"fragId\": " << pkt.fragmentId
                      << ", \"success\": " << (pkt.success ? "true" : "false")
                      << ", \"rssi\": " << std::setprecision(1) << pkt.rssiDbm
                      << ", \"srcX\": " << std::setprecision(1) << pkt.srcX
                      << ", \"srcY\": " << pkt.srcY
                      << ", \"srcZ\": " << pkt.srcZ << "}";
            firstPacket = false;
        }
        if (!firstPacket) {
            data_json << "\n";
        }
    }
    data_json << "  ]\n";
    data_json << "}";

    std::string json_data = data_json.str();

    // Write full result HTML file with embedded data and canvas rendering
    std::ofstream out(GetPath("wsn-uav-result.html"));
    if (!out.is_open()) {
        NS_LOG_ERROR("Failed to open wsn-uav-result.html");
        return;
    }

    // Write complete HTML with Canvas visualization + zoom
    out << "<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='style=device-width,initial-scale=1'>";
    out << "<title>WSN-UAV Result Visualization</title><style>";
    out << "*{margin:0;padding:0;box-sizing:border-box}";
    out << "body{font-family:Arial,sans-serif;background:#1a1a1a;color:#fff;height:100vh}";
    out << ".container{display:grid;grid-template-columns:1fr 150px;height:100vh}";
    out << ".canvas-area{background:#222;display:flex;flex-direction:column;position:relative}";
    out << "canvas{flex:1;width:100%;display:block}";
    out << ".zoom-controls{position:absolute;top:10px;right:10px;background:#333;border-radius:5px;padding:5px;z-index:10}";
    out << ".zoom-btn{background:#667eea;color:#fff;border:none;width:28px;height:28px;border-radius:3px;cursor:pointer;font-size:14px;margin:2px}";
    out << ".zoom-btn:hover{background:#764ba2}";
    out << ".zoom-level{text-align:center;font-size:9px;color:#999;width:40px}";
    out << ".controls{background:#333;padding:8px;max-height:110px;overflow-y:auto;font-size:11px}";
    out << ".controls>button{margin:3px 0;display:block;padding:5px 8px;font-size:10px;height:24px}";
    out << ".slider-box{margin:6px 0;font-size:10px}";
    out << ".sidebar{background:#2a2a2a;padding:10px;overflow-y:auto;border-left:1px solid #444;font-size:11px}";
    out << ".info{margin:8px 0}.info-title{font-weight:bold;color:#667eea;margin-bottom:3px;font-size:10px}";
    out << ".info-value{color:#999;margin:2px 0;font-size:9px;word-break:break-word}";
    out << "input[type=range]{width:100%;cursor:pointer;height:16px}";
    out << "button{background:#667eea;color:#fff;border:none;padding:5px 8px;border-radius:3px;cursor:pointer;width:100%;font-size:10px}";
    out << "button:hover{background:#764ba2}";
    out << "label{display:flex;align-items:center;margin:4px 0;cursor:pointer;font-size:10px}";
    out << "input[type=checkbox]{margin-right:6px;cursor:pointer;width:14px;height:14px}";
    out << "</style></head><body><div class='container'>";
    out << "<div class='canvas-area'><canvas id='canvas'></canvas>";
    out << "<div class='zoom-controls'><button class='zoom-btn' onclick='zoomIn()'>+</button>";
    out << "<div class='zoom-level' id='zoomLabel'>100%</div>";
    out << "<button class='zoom-btn' onclick='zoomOut()'>−</button></div>";
    out << "<div class='controls'>";
    out << "<button onclick='play()'>▶ Play</button><button onclick='pause()'>⏸ Pause</button>";
    out << "<button onclick='reset()'>⏮ Reset</button>";
    out << "<div class='slider-box'>Time:<span id='timeLabel'>0.0</span>/<span id='maxLabel'>100</span>s</div>";
    out << "<input id='slider' type='range' min='0' max='100' value='0' step='0.1' onchange='seek(this.value)'>";
    out << "</div></div>";
    out << "<div class='sidebar'>";
    out << "<div class='info'><div class='info-title'>▼ Result</div>";
    out << "<div class='info-value' id='info1'></div>";
    out << "<div class='info-value' id='info2'></div>";
    out << "</div>";
    out << "<div class='info'><div class='info-title'>▼ Layers</div>";
    out << "<label><input type='checkbox' id='c1' checked onchange='render()'>Grid</label>";
    out << "<label><input type='checkbox' id='c2' checked onchange='render()'>Nodes</label>";
    out << "<label><input type='checkbox' id='c3' checked onchange='render()'>Traj</label>";
    out << "<label><input type='checkbox' id='c4' checked onchange='render()'>Cand</label>";
    out << "<label><input type='checkbox' id='c5' checked onchange='render()'>TX (UAV+G2G)</label>";
    out << "<label><input type='checkbox' id='c6' onchange='render()'>Drop</label>";
    out << "</div>";
    out << "<div class='info'><div class='info-title'>▼ Legend</div>";
    out << "<div style='font-size:9px;line-height:1.6'>";
    out << "<div style='margin-bottom:6px;border-bottom:1px solid #666;padding-bottom:4px'><b>Packets</b></div>";
    out << "<div style='color:#64C864'>🟢 UAV Success</div>";
    out << "<div style='color:#FF6464'>🔴 UAV Drop</div>";
    out << "<div style='color:#FFFF64'>🟡 G2G Success</div>";
    out << "<div style='color:#C89664'>🟠 G2G Drop</div>";
    out << "<div style='margin-top:6px;margin-bottom:6px;border-bottom:1px solid #666;padding-bottom:4px'><b>Nodes (Fragments)</b></div>";
    out << "<div style='color:#0000FF'>🔵 0 frags</div>";
    out << "<div style='color:#00FF00'>🟢 50%</div>";
    out << "<div style='color:#FFFF00'>🟡 100%</div>";
    out << "</div></div>";
    out << "<button onclick='exp()' style='margin-top:6px;padding:4px 6px;font-size:9px'>📥 JSON</button>";
    out << "</div></div>";
    out << "<script>";
    out << "const d=" << json_data << ";";
    out << "const c=document.getElementById('canvas');const ctx=c.getContext('2d');";
    out << "let t=0,p=false,zm=200,ox=0,oy=0;";
    out << "c.width=c.offsetWidth;c.height=c.offsetHeight;";
    out << "window.addEventListener('resize',()=>{c.width=c.offsetWidth;c.height=c.offsetHeight;});";
    out << "c.addEventListener('wheel',(e)=>{e.preventDefault();const oldZm=zm;zm*=e.deltaY<0?1.1:0.9;zm=Math.max(0.1,Math.min(500,zm));const zoomFactor=zm/oldZm;ox=e.x+(ox-e.x)*zoomFactor;oy=e.y+(oy-e.y)*zoomFactor;document.getElementById('zoomLabel').textContent=(zm/10).toFixed(0)+'x';render();});";
    out << "let dx=0,dy=0;c.addEventListener('mousedown',(e)=>{dx=e.x;dy=e.y;});";
    out << "c.addEventListener('mousemove',(e)=>{if(e.buttons){ox+=e.x-dx;oy+=e.y-dy;dx=e.x;dy=e.y;render();}});";
    out << "function zoomIn(){const oldZm=zm;zm=Math.min(500,zm*1.2);const zoomFactor=zm/oldZm;ox=c.width/2+(ox-c.width/2)*zoomFactor;oy=c.height/2+(oy-c.height/2)*zoomFactor;document.getElementById('zoomLabel').textContent=(zm/10).toFixed(0)+'x';render();}";
    out << "function zoomOut(){const oldZm=zm;zm=Math.max(0.1,zm/1.2);const zoomFactor=zm/oldZm;ox=c.width/2+(ox-c.width/2)*zoomFactor;oy=c.height/2+(oy-c.height/2)*zoomFactor;document.getElementById('zoomLabel').textContent=(zm/10).toFixed(0)+'x';render();}";
    out << "function gp(x,y){const g=d.config.gridSize;const s=d.config.gridSpacing;const gridMax=s*(g-1);const pd=10;const baseW=c.width-2*pd;const baseH=c.height-2*pd;const sc=Math.min(baseW,baseH)/gridMax*zm;const offsetX=ox+pd+(gridMax/2)*sc/s;const offsetY=oy+pd+(gridMax/2)*sc/s;return{x:offsetX+x*sc/s,y:offsetY+y*sc/s};}";
    out << "function render(){";
    out << "ctx.fillStyle='#1a1a1a';ctx.fillRect(0,0,c.width,c.height);";
    out << "const g=d.config.gridSize;const s=d.config.gridSpacing;";
    out << "if(document.getElementById('c1').checked){ctx.strokeStyle='#444';ctx.lineWidth=0.5;";
    out << "for(let i=0;i<g;i++){const p1=gp(0,i*s);const p2=gp((g-1)*s,i*s);ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke();}";
    out << "for(let i=0;i<g;i++){const p3=gp(i*s,0);const p4=gp(i*s,(g-1)*s);ctx.beginPath();ctx.moveTo(p3.x,p3.y);ctx.lineTo(p4.x,p4.y);ctx.stroke();}}";
    out << "if(document.getElementById('c6').checked && d.packets){ctx.fillStyle='rgba(255,0,0,0.4)';ctx.strokeStyle='#FF0000';ctx.lineWidth=1.5;";
    out << "for(let pk of d.packets){if(pk.t>t)break;if(!pk.success){const dst=d.nodes[pk.dst];if(dst){const p=gp(dst.x,dst.y);if(p.x>-50&&p.x<c.width+50&&p.y>-50&&p.y<c.height+50){ctx.beginPath();ctx.moveTo(p.x-4,p.y-4);ctx.lineTo(p.x+4,p.y+4);ctx.stroke();ctx.beginPath();ctx.moveTo(p.x+4,p.y-4);ctx.lineTo(p.x-4,p.y+4);ctx.stroke();}}}}}";
    out << "if(document.getElementById('c5').checked && d.packets){let renderCount=0;const fadeWindow=2.0;";
    out << "for(let pk of d.packets){if(pk.t>t)break;const dst=d.nodes[pk.dst];if(dst){";
    out << "const age=t-pk.t;const fadeFactor=Math.max(0,1-age/fadeWindow);";
    out << "const alpha=Math.max(0.1,fadeFactor*0.8);";
    out << "if(pk.type==='uav'){";
    out << "ctx.strokeStyle=pk.success?`rgba(100,200,100,${alpha})`:`rgba(255,100,100,${alpha})`;";
    out << "}else if(pk.type==='g2g'){";
    out << "ctx.strokeStyle=pk.success?`rgba(255,255,100,${alpha})`:`rgba(200,150,100,${alpha})`;";  // Yellow for successful G2G, muted yellow for failed
    out << "}";
    out << "ctx.lineWidth=1.5;";
    out << "const p1=gp(pk.srcX,pk.srcY);const p2=gp(dst.x,dst.y);ctx.beginPath();ctx.moveTo(p1.x,p1.y);ctx.lineTo(p2.x,p2.y);ctx.stroke();renderCount++;}}}";
    out << "ctx.fillStyle='#FFFF00';ctx.font='12px monospace';ctx.fillText('TX packets:'+d.packets.length+' (t='+t.toFixed(1)+')',10,20);";
    out << "if(document.getElementById('c3').checked){ctx.strokeStyle='#667eea';ctx.lineWidth=2;ctx.globalAlpha=0.6;ctx.beginPath();let f=true;";
    out << "for(let pt of d.uavTrajectory){if(pt.t>t)break;const p=gp(pt.x,pt.y);if(f){ctx.moveTo(p.x,p.y);f=false;}else{ctx.lineTo(p.x,p.y);}}";
    out << "ctx.stroke();ctx.globalAlpha=1;}";
    out << "if(document.getElementById('c2').checked){";
    out << "const nodeFrags={};";
    out << "for(let pk of d.packets){if(pk.t>t)break;if(pk.success){if(!nodeFrags[pk.dst])nodeFrags[pk.dst]=new Set();nodeFrags[pk.dst].add(pk.fragId);}}";
    out << "for(let nid in d.nodes){const n=d.nodes[nid];if(!n)continue;const p=gp(n.x,n.y);if(p.x>-50&&p.x<c.width+50&&p.y>-50&&p.y<c.height+50){";
    out << "let col='#4A5B7F';let r=6;";  // Muted dark blue for no fragments
    out << "const fragCount=nodeFrags[nid]?nodeFrags[nid].size:0;";
    out << "if(fragCount>0){";
    out << "const maxFrags=d.config.numFragments;const ratio=Math.min(1,fragCount/maxFrags);";
    out << "const hue=Math.floor(240-ratio*240);col=`hsl(${hue},60%,55%)`;r=6+ratio*2;}";  // Reduced saturation from 100% to 60%, lightness from 50% to 55%
    out << "ctx.fillStyle=col;ctx.beginPath();ctx.arc(p.x,p.y,r,0,Math.PI*2);ctx.fill();";
    out << "if(n.isDetectionNode){ctx.strokeStyle='#C85A54';ctx.lineWidth=3;ctx.beginPath();ctx.arc(p.x,p.y,r+3,0,Math.PI*2);ctx.stroke();}";  // Red outline for detection node
    out << "if(document.getElementById('c4').checked && n.isCandidate){ctx.strokeStyle='#9E8C42';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,r+2,0,Math.PI*2);ctx.stroke();}}}}";  // Muted yellow for candidates
    out << "let up=null;for(let i=0;i<d.uavTrajectory.length;i++){if(d.uavTrajectory[i].t>t){if(i>0){const p1=d.uavTrajectory[i-1];const p2=d.uavTrajectory[i];const tt=(t-p1.t)/(p2.t-p1.t);up={x:p1.x+(p2.x-p1.x)*tt,y:p1.y+(p2.y-p1.y)*tt};}break;}}";
    out << "if(!up && d.uavTrajectory.length>0)up=d.uavTrajectory[d.uavTrajectory.length-1];";
    out << "if(up){const p=gp(up.x,up.y);if(p.x>-50&&p.x<c.width+50&&p.y>-50&&p.y<c.height+50){ctx.fillStyle='#667eea';ctx.beginPath();ctx.arc(p.x,p.y,8,0,Math.PI*2);ctx.fill();";
    out << "ctx.strokeStyle='rgba(102,126,234,0.3)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p.x,p.y,16,0,Math.PI*2);ctx.stroke();}}}";
    out << "function upd(){document.getElementById('timeLabel').textContent=t.toFixed(1);";
    out << "document.getElementById('maxLabel').textContent=d.config.simTime.toFixed(1);";
    out << "document.getElementById('slider').max=d.config.simTime;";
    out << "document.getElementById('info1').textContent=d.config.detected?'✓ Detected':'✗ Not detected';";
    out << "if(d.config.detected)document.getElementById('info1').textContent+=' @ '+d.config.detectionTime.toFixed(1)+'s';";
    out << "document.getElementById('info2').textContent='Path: '+d.config.uavPathLength.toFixed(0)+'m';";
    out << "render();}";
    out << "function anim(){if(p){t+=0.05;if(t>=d.config.simTime)p=false;document.getElementById('slider').value=t;upd();}requestAnimationFrame(anim);}";
    out << "function play(){p=true;}function pause(){p=false;}function reset(){t=0;p=false;ox=0;oy=0;zm=200;document.getElementById('slider').value=0;document.getElementById('zoomLabel').textContent='20x';upd();}";
    out << "function seek(v){t=parseFloat(v);upd();}";
    out << "function exp(){const j=JSON.stringify(d,null,2);const b=new Blob([j],{type:'application/json'});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download='wsn-uav-result.json';a.click();URL.revokeObjectURL(u);}";
    out << "upd();anim();";
    out << "</script></body></html>";

    out.close();
    NS_LOG_INFO("Visualization written to " << GetPath("wsn-uav-result.html"));
}

}  // namespace uav
}  // namespace wsn
}  // namespace ns3
