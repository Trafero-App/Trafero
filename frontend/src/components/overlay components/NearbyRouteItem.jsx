import {IoMdEye, IoMdEyeOff} from 'react-icons/io'
import { MapContext } from '../../App'
import { useContext, useState, useEffect } from 'react'

const NearbyRouteItem = ({
    routeData, previewedIds,
    setPreviewedIds
}) => {

    const value = useContext(MapContext)
    const map = value.mapRef.current
    const {chosenBusIds, setChosenBusIds} = value
    const {setChosenRouteIntervalId} = value
    const {chosenRoute, setChosenRoute, fetchRouteData} = value

    const [isBeingShown, setBeingShown] = useState(false)

    const id = `route-${routeData.route_id}`
    //listens to value of isBeingShown
    useEffect(() => {
        const vehicle_ids=routeData.vehicles.map((e) => e.id)
        if(isBeingShown){
            //adds it to previewed ids
            setPreviewedIds(previewedIds.concat([routeData.route_id]))
            //shows line
            map.addSource(id,{
                type: 'geojson',
                data: routeData.line
            })
            map.addLayer({
                id: `${id}-layer`,
                type: "line",
                source: id,
                layout: {
                    "line-join": "round",
                    "line-cap": "round"
                }, 
                paint: {
                    "line-color": "#14A202", // lime color
                    "line-width": 4 // thin line
                }
            },'bus-stops-layer')
            if(!vehicle_ids.every((e) => chosenBusIds.includes(e))){
                setChosenBusIds(chosenBusIds.concat(vehicle_ids))
            }
        }
        else{
            //remove route from previewed id's
            setPreviewedIds(previewedIds.filter((e) => e!=routeData.route_id))
            //hides line
            if(map.getLayer( `${id}-layer`)) map.removeLayer( `${id}-layer`)
            if(map.getSource(id)) map.removeSource(id)
            if(chosenBusIds) setChosenBusIds(chosenBusIds.filter((e) => !vehicle_ids.includes(e)))
        }
    },[isBeingShown])

    //this useEffect runs on render, checks if routes were already highlighted for some reason (maybe we chose a bus and went back to showing routes)
    useEffect(() => {
        if(previewedIds.includes(routeData.route_id)){
            setBeingShown(true)
        }
    },[previewedIds])

    return (
        <div 
        className='flex items-center h-12 hover:bg-gray1 transition duration-200 cursor-pointer'
        onClick={() => {
            setChosenRoute(routeData)
            setChosenRouteIntervalId(setInterval(() => {
                fetchRouteData(routeData.route_id)
            },2000))
        }}
        >  
            <div className=' flex-shrink-0 h-10 w-[5px] bg-lime'/>    
            <div 
            className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-4 text-sm h-12'
            >
                <h1 className='font-semibold'>{routeData.route_name}</h1>
                <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description}</h1>
            </div>
            <div 
            className='flex justify-center items-center h-12 w-12 min-w-12'
            >
                <div
                className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
                onClick = {(e) => {
                    e.stopPropagation()
                    setBeingShown(!isBeingShown)
                }}
                >
                    {!isBeingShown ? 
                    <IoMdEyeOff
                    className='h-6 w-6'
                    />
                    :
                    <IoMdEye
                    className='h-6 w-6'
                    />
                    }
                </div>
            </div>
        </div>
    )
}

export default NearbyRouteItem