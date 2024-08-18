import React, { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContext } from '../../App'
import { MdDelete } from 'react-icons/md'

const SavedRouteItem = ({routeData, isEditing}) => {

    const navigate = useNavigate()
    const value = useContext(MapContext)
    const {savedRoutes, setSavedRoutes} = value 

    return (
        <div 
        className='flex h-12 hover:bg-gray1 transition duration-200 cursor-pointer'
        onClick={() => {
            if(!isEditing){
                navigate(`/search/route/${routeData.route_id}`)
            }
        }}
        >      
            <div 
            className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-4 text-sm h-12'
            >
                <h1 className='font-semibold'>{routeData.route_name}</h1>
                <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description}</h1>
            </div>
            <div 
            className='flex justify-center items-center h-12 w-12 min-w-12'
            >
                {
                isEditing &&
                <div
                className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
                onClick={() => {
                    setSavedRoutes(savedRoutes.filter((e) => e.route_id!=routeData.route_id))
                }}
                >
                    <MdDelete
                    className='h-6 w-6'
                    />
                </div>
                }
            </div>
        </div>
    )
}

export default SavedRouteItem