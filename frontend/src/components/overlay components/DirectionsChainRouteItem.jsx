import {IoMdEye, IoMdEyeOff} from 'react-icons/io'
import {FaLink} from 'react-icons/fa6'
import { MapContext } from '../../App'
import { useContext, useState, useEffect } from 'react'

const minutesToText= (minutes) => {
    if(minutes==0) return '0m'
    if(minutes%60==0) return `${Math.floor(minutes/60)}h`
    if(minutes<60) return `${minutes}m`
    return `${Math.floor(minutes/60)}h ${minutes%60}m`
  }

const DirectionsChainRouteItem = ({
    routeData,
    previewedIds,setPreviewedIds
}) => {

    routeData.route_id=routeData.route_id1+"+"+routeData.route_id2
    routeData.vehicles=routeData.vehicles1.concat(routeData.vehicles2)

    const value = useContext(MapContext)
    const map = value.mapRef.current
    const {chosenBusIds, setChosenBusIds} = value
    const {setChosenRouteIntervalId} = value
    const {chosenRoute, setChosenRoute, fetchRouteData} = value

    const route1 = {
        route_id: routeData.route_id1,
        route_name: routeData.route_name1,
        description: routeData.description1,
        vehicles: routeData.vehicles1,
        line: routeData.line1
    }

    const route2 = {
        route_id: routeData.route_id2,
        route_name: routeData.route_name2,
        description: routeData.description2,
        vehicles: routeData.vehicles2,
        line: routeData.line2
    }

    const [isBeingShown, setBeingShown] = useState(false)

    const id = `route-${routeData.route_id}`
    //listens to value of isBeingShown
    useEffect(() => {
        const vehicle_ids=routeData.vehicles.map((e) => e.id)
        if(isBeingShown){
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
                    "line-color": ['match',['get','order'],
                    1, '#1487D8',
                    '#7D4DD0'
                ],
                    "line-width": 4 // thin line
                }
            },'bus-stops-layer')
            if(!previewedIds.includes(routeData.route_id)){
                setChosenBusIds(chosenBusIds.concat(vehicle_ids))
                setPreviewedIds(previewedIds.concat([routeData.route_id]))
            }
        }
        else{
            //hides line
            if(map.getLayer( `${id}-layer`)) map.removeLayer( `${id}-layer`)
            if(map.getSource(id)) map.removeSource(id)
            if(chosenBusIds) setChosenBusIds(chosenBusIds.filter((e) => !vehicle_ids.includes(e)))
            setPreviewedIds(previewedIds.filter((e) => e!=routeData.route_id))
        }
    },[isBeingShown])

    //this useEffect runs on render, checks if routes were already highlighted for some reason (maybe we chose a bus and went back to showing routes)
    useEffect(() => {
        if(previewedIds.includes(routeData.route_id)){
            setBeingShown(true)
        }
    },[previewedIds])

    return (
        <div className='relative group flex h-24 cursor-pointer '>      
            <div className='w-full'>
                <div 
                className='w-full flex items-end hover:bg-gray1 transition duration-200'
                onClick={() => {
                    setChosenRoute(route1)
                    setChosenRouteIntervalId(setInterval(() => {
                        fetchRouteData(route1.route_id)
                    },2000))
                }}
                >
                    <div className='h-11 w-[5px] bg-skyblue'/>
                    <div 
                    className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-[40px] pr-[6.5rem] text-sm h-12'
                    >
                        <h1 className='font-semibold truncate'>{routeData.route_name1}</h1>
                        <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description1}</h1>
                    </div>
                </div>
                <div 
                className='w-full flex items-start hover:bg-gray1 transition duration-200'
                onClick={() => {
                    setChosenRoute(route2)
                    setChosenRouteIntervalId(setInterval(() => {
                        fetchRouteData(route2.route_id)
                    },2000))
                }}
                >
                    <div className='h-11 w-[5px] bg-darkblue'/>
                    <div 
                    className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-[40px] pr-[6.5rem] text-sm h-12'
                    >
                        <h1 className='font-semibold truncate'>{routeData.route_name2}</h1>
                        <h1 className='text-ellipsis text-nowrap overflow-hidden pr-2'>{routeData.description2}</h1>
                    </div>
                </div>
            </div>
            <div 
            className='flex absolute right-0 justify-between items-center h-24 w-full pointer-events-none'
            >
                <div className='flex justify-center items-center h-8 w-12'>
                    <FaLink
                    className='h-[1.25rem] w-[1.25rem]'
                    />
                </div>
                <div className='flex items-center'>
                    <div className='rounded-xl bg-gray1 group-hover:bg-gray2 transition duration-200 mr-2'>
                        <h1 className='px-3 font-semibold'>{minutesToText(routeData.eta)}</h1>
                    </div>
                    <div
                    className='mr-2 flex justify-center items-center h-8 w-8 rounded-[2rem] bg-gray1 hover:bg-gray2 transition duration-200 pointer-events-auto'
                    onClick = {() => setBeingShown(!isBeingShown)}
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
        </div>
    )
}

export default DirectionsChainRouteItem