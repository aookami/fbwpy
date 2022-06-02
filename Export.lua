

function LuaExportStart()
	socket = require("socket")
	host = "localhost"
	port = 8075
	udp = socket.udp()
    udp:settimeout(0)
    udp:setoption('reuseaddr',true)
    udp:setpeername('localhost', 8075)
end

function LuaExportAfterNextFrame()
    local ias = LoGetIndicatedAirSpeed()
    local accelUnits = LoGetAccelerationUnits() -- xyz
    local vectorVelocities = LoGetVectorVelocity()
    local angularVelocities = LoGetAngularVelocity()
    local engine = LoGetEngineInfo()
    local helData = LoGetHelicopterFMData()

    udp:send(string.format("ias=%.4f ,accy=%.4f, vvx=%.4f,vvy=%.4f,vvz=%.4f,avx=%.4f,avy=%.4f,avz=%.4f,erpmr=%.4f,erpml=%.4f, aay=%.4f",
       ias , accelUnits.y, vectorVelocities.x, vectorVelocities.y, vectorVelocities.z, angularVelocities.x, angularVelocities.y, angularVelocities.z,  engine.RPM.right, engine.RPM.left, helData.angular_acceleration.y))
end

function LuaExportStop()
	connection:close()
end
