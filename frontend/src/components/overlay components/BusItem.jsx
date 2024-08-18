import { MapContext } from "../../App";
import { useContext } from "react";
import { FaBusAlt } from "react-icons/fa";

const capitalizeFirstLetter = (str) => {
    if (!str) return str;
    return str.charAt(0).match(/[a-zA-Z]/) ? str.charAt(0).toUpperCase() + str.slice(1) : str;
};

const minutesToText= (minutes) => {
    if(minutes==0) return '0m'
    if(minutes%60==0) return `${Math.floor(minutes/60)}h`
    if(minutes<60) return `${minutes}m`
    return `${Math.floor(minutes/60)}h ${minutes%60}m`
}

const BusItem = ({vehicle, setChosenBusIntervalId}) => {

    const {status, license_plate} = vehicle
    const value = useContext(MapContext)
    const map=value.mapRef.current
    const {busData, setSingleChosenBusId, setChosenBusDataLoading, setLookingAtBus,fetchChosenBusData} = value

    const handleBusItemClick = () => {  
        if(busData.filter((e) => e.properties.id == vehicle.id).length==0){
            //bus is no longer on the map
            return;
        }
        setLookingAtBus(true)
        const clickedBus = busData.filter((e) => e.properties.id == vehicle.id)[0] //this is the feature object that was clicked on
        map.flyTo({center: clickedBus.geometry.coordinates, zoom: Math.max(16, map.getZoom())})//flyTo without setting the zoom keeps original zoom
        setSingleChosenBusId(clickedBus.properties.id)
        setChosenBusDataLoading(true)
        fetchChosenBusData(clickedBus.properties.id)
        const id=setInterval(() => {
            fetchChosenBusData(clickedBus.properties.id)
        },2000)
        setChosenBusIntervalId(id)
    }

    return (
        <div 
        className='flex justify-between items-center pr-4 text-sm h-14 lg:h-12 hover:bg-gray1 transition duration-200 cursor-pointer'
        onClick={handleBusItemClick}
        >
            <div className='flex'>
                <div className='h-14 w-14 lg:h-12 lg:w-12 flex justify-center items-center'>
                    <FaBusAlt className='h-6 w-6'/>
                </div>
                <div className='flex flex-col justify-center'>
                    <h1 className='font-bold'>{license_plate}</h1>
                    {vehicle.passed!=undefined &&
                    <h1 className={`px-2 text-white rounded-md ${status=='active' ? 'bg-active-green' : status=='unavailable' ? 'bg-unavailable-red' : status=='waiting' ? 'bg-waiting-yellow' : status=='inactive' ? 'bg-black' : 'bg-gray4'}`}>{capitalizeFirstLetter(status)}</h1>
                    }
                </div>
            </div>
            
            {vehicle.passed!=undefined ?
            <h1 className={`px-3 h-8 lg:h-7 flex items-center text-white rounded-xl ${vehicle.passed ? 'bg-gray4' : 'bg-blue3'}`}>{vehicle.passed ? 'Passed' : `${minutesToText(vehicle.expected_time)}`}</h1>
            :
            <h1 className={`px-3 h-8 lg:h-7 flex items-center text-white rounded-xl ${status=='active' ? 'bg-active-green' : status=='unavailable' ? 'bg-unavailable-red' : status=='waiting' ? 'bg-waiting-yellow' : status=='inactive' ? 'bg-black' : 'bg-gray4'}`}>{capitalizeFirstLetter(status)}</h1>
            }
        </div>
    )
}

export default BusItem