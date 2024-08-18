import { MapContext } from '../../App'
import { useContext, useState, useEffect } from 'react'

import {IoMdEye, IoMdEyeOff} from 'react-icons/io'
import { IoClose } from 'react-icons/io5'
import { MdDelete } from 'react-icons/md'

const DriverRouteItem = ({
    routeData, isEditing, chosenRoute, setChosenRoute, handleRouteItemClick
}) => {

    const value = useContext(MapContext)
    const map = value.mapRef.current
    const {routes, setRoutes} = value

    const [isBeingShown, setBeingShown] = useState(false)

    const id = `driver-route-${routeData.route_id}`
    //listens to value of isBeingShown
    useEffect(() => {
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
                    "line-color": "#666666", // gray color
                    "line-width": 4 // thin line
                }
            })
        }
        else{
            //hides line
            if(map.getLayer( `${id}-layer`)) map.removeLayer( `${id}-layer`)
            if(map.getSource(id)) map.removeSource(id)
        }
    },[isBeingShown])

    //this useEffect listens to isEditing and sets isBeingShown to false
    useEffect(() => {
        if(isEditing || chosenRoute){
            setBeingShown(false)
        }
    },[isEditing, chosenRoute])

    return (
        chosenRoute ?
        <div className={`flex h-12 ${chosenRoute.route_id==routeData.route_id ? 'bg-gray2' : 'hover:bg-gray1'} transition duration-200 cursor-pointer`}>
            <div 
            className={`flex flex-col justify-center overflow-hidden w-full pointer-events-auto ${chosenRoute.route_id==routeData.route_id ? 'pl-4' : 'px-4'} text-sm h-12`}
            onClick={() => handleRouteItemClick(routeData)}
            >
                <h1 className='font-semibold'>{routeData.route_name}</h1>
                <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description}</h1>
            </div>
            {chosenRoute.route_id==routeData.route_id &&
            <div className='flex h-12 w-12 min-w-12 justify-center items-center'>
                    <div 
                    className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray3 transition duration-200'
                    onClick={() => setChosenRoute(null)}
                    >
                        <IoClose className='h-6 w-6'/>
                    </div>
            </div>
            } 
        </div>
        :
        <div className='flex h-12 hover:bg-gray1 transition duration-200 cursor-pointer'>      
            <div 
            className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-4 text-sm h-12'
            onClick={() => handleRouteItemClick(routeData)}
            >
                <h1 className='font-semibold'>{routeData.route_name}</h1>
                <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description}</h1>
            </div>
            <div 
            className='flex justify-center items-center h-12 w-12 min-w-12'
            >
                {
                isEditing ?
                <div
                className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
                onClick={() => {setRoutes(routes.filter((e) => e!=routeData))}}
                >
                    <MdDelete
                    className='h-6 w-6'
                    />
                </div>
                :
                <div
                className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
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
                }
            </div>
        </div>
    )
}

export default DriverRouteItem