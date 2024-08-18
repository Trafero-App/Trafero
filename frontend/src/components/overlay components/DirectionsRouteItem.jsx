import {IoMdEye, IoMdEyeOff} from 'react-icons/io'
import { MapContext } from '../../App'
import { useContext, useState, useEffect } from 'react'
import * as turf from '@turf/turf'

const minutesToText= (minutes) => {
    if(minutes==0) return '0m'
    if(minutes%60==0) return `${Math.floor(minutes/60)}h`
    if(minutes<60) return `${minutes}m`
    return `${Math.floor(minutes/60)}h ${minutes%60}m`
  }
  

const DirectionsRouteItem = ({
    routeData,
    startingPoint, destination,
    previewedIds,setPreviewedIds
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
            //shows line that cut from start and end
            const start=turf.nearestPointOnLine(routeData.line,{type: 'Point', coordinates: startingPoint.coordinates})
            const end = turf.nearestPointOnLine(routeData.line,{type: 'Point', coordinates: destination.coordinates})
            //give index is index of string line (=length-1 if nearest point was last line)
            const newCoordinates = [start.geometry.coordinates].concat(routeData.line.features[0].geometry.coordinates.slice(start.properties.index+1,end.properties.index+1),[end.geometry.coordinates])
            map.addSource(id,{
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [
                        {
                            type: 'Feature',
                            properties: {},
                            geometry: {
                                coordinates: newCoordinates,
                                type: 'LineString'
                            }
                        }
                    ]
                }
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
            if(!previewedIds.includes(routeData.route_id)){
                setChosenBusIds(chosenBusIds.concat(vehicle_ids))
                setPreviewedIds(previewedIds.concat([routeData.route_id]))
            }
        }
        else{
            //hides line
            if(map.getLayer(`${id}-layer`)) map.removeLayer( `${id}-layer`)
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
        <div className='group flex h-12 hover:bg-gray1 transition duration-200 cursor-pointer'>   
            <div 
            className='flex w-full items-center justify-between'
            onClick={() => {
                setChosenRoute(routeData)
                setChosenRouteIntervalId(setInterval(() => {
                    fetchRouteData(routeData.route_id)
                },2000))
            }}
            >
                <div className=' flex-shrink-0 h-10 w-[5px] bg-lime'/>
                <div 
                className='pl-2 flex flex-col justify-center overflow-hidden w-full pointer-events-auto text-sm h-12'
                
                >
                    <h1 className='font-semibold'>{routeData.route_name}</h1>
                    <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description}</h1>
                </div>
                <div className='flex items-center'>
                    <div className='ml-2 rounded-xl bg-gray1 group-hover:bg-gray2 transition duration-200'>
                        <h1 className='px-3 font-semibold'>{minutesToText(routeData.eta)}</h1>
                    </div>
                    <div 
                    className='flex justify-center items-center h-12 w-12 min-w-12'
                    >
                        <div
                        className='flex justify-center items-center h-8 w-8 rounded-[2rem] bg-gray1 hover:bg-gray2 transition duration-200'
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
            </div>         
        </div>
    )
}

export default DirectionsRouteItem