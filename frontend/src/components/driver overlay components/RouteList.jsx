import { useState, useContext } from "react"
import { MapContext } from "../../App"
import {IoIosArrowDown, IoIosArrowUp, IoMdClose} from 'react-icons/io'
import { MdEdit } from "react-icons/md"

import DriverRouteItem from './DriverRouteItem'

const RouteList = ({
    routes,
    isSharingLiveLocation,
    handleRouteItemClick,
    chosenRoute, setChosenRoute
}) => {

    const value = useContext(MapContext)
    const map = value.mapRef.current

    const [isShowingRoutes, setShowingRoutes] = useState(false)
    const [isEditing, setEditing] = useState(false)

    return (
        <div className={`bg-white w-full max-w-96 pointer-events-auto rounded-xl shadow-md ${!isShowingRoutes ? 'opacity-90 hover:opacity-100' : 'pb-3'}`}>
            <div className={`h-14 lg:h-12 flex justify-between items-center ${isShowingRoutes && 'border-b-2 border-gray2'}`}>
                <div className='w-14 lg:w-12 flex justify-center items-center'>
                {(isShowingRoutes && !isSharingLiveLocation && routes.length!=0) &&
                (isEditing ?
                <IoMdClose
                className='w-6 h-6 text-gray2 hover:text-gray4 cursor-pointer transition-duration-200'
                onClick={() => setEditing(!isEditing)}
                />
                :
                <MdEdit
                className='w-6 h-6 text-gray2 hover:text-gray4 cursor-pointer transition-duration-200'
                onClick={() => setEditing(!isEditing)}
                />
                )
                }
                </div>
                <h1 className='font-semibold'>My Routes</h1>
                <div className='w-14 lg:w-12 flex justify-center items-center'>
                {
                !isEditing &&
                (isShowingRoutes ?
                <IoIosArrowUp
                className='w-6 h-6 text-gray2 hover:text-gray4 cursor-pointer transition-duration-200'
                onClick={() => {
                    setShowingRoutes(!isShowingRoutes)
                    routes.forEach((route) => {
                        const id = `driver-route-${route.route_id}`
                        //hides line
                        if(map.getLayer( `${id}-layer`)) map.removeLayer( `${id}-layer`)
                        if(map.getSource(id)) map.removeSource(id)
                    })
                }}
                />
                :
                <IoIosArrowDown 
                className='w-6 h-6 text-gray2 hover:text-gray4 cursor-pointer transition-duration-200'
                onClick={() => setShowingRoutes(!isShowingRoutes)}
                />
                )
                }
                </div>
            </div>
            {
            isShowingRoutes &&
            (
            routes.length==0 ?
            //driver has no routes
            <div className='h-14 flex items-center pt-3'>
                <h1 className='text-sm p-3'>Click on the + button in the bottom left corner of a route page to add it</h1>
            </div>
            :
            <div className={`mt-3 ${routes.length>3 && 'h-36 scrollable'} overflow-auto`}>
                {routes.map((element,index) => <DriverRouteItem key={index} chosenRoute={chosenRoute} setChosenRoute={setChosenRoute} isEditing={isEditing} routeData={element} handleRouteItemClick={handleRouteItemClick}/>)}
            </div>
            )
            }
        </div>
    )
}

export default RouteList