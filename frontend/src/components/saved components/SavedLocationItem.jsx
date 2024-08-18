import { useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContext } from '../../App'
import { FaMapMarkerAlt, FaGraduationCap, FaBus, FaBriefcase } from 'react-icons/fa'
import { FaHouse, FaPerson } from 'react-icons/fa6'
import {MdDelete} from 'react-icons/md'

const SavedLocationItem = ({data, isEditing}) => {

    const navigate=useNavigate()
    const value = useContext(MapContext)
    const {savedLocations, setSavedLocations} = value

    const handleLocationItemClick = () => {
        if(value.isMapLoaded && !isEditing){
            value.mapRef.current.flyTo(({center: data.coordinates, zoom: Math.max(13,value.mapRef.current.getZoom())}))
            navigate('/map')
        }
    }

    return (
        !isEditing ?
        <div 
        className='flex-shrink-0 ml-3 flex justify-between items-center h-12 max-w-[10rem] rounded-[2rem] border-2 border-gray1 hover:bg-gray1 transition duration-200 cursor-pointer pl-3 pr-4'
        onClick={handleLocationItemClick}
        >
            <div className='h-12 w-6 flex justify-center items-center'>
                {data.icon=='home' ?
                <FaHouse className='h-5 w-5'/>
                :
                data.icon=='school' ?
                <FaGraduationCap className='h-6 w-6'/>
                :
                data.icon=='work' ?
                <FaBriefcase className='h-5 w-5'/>
                :
                data.icon=='person' ?
                <FaPerson className='h-6 w-6'/>
                :
                data.icon=='bus' ?
                <FaBus className='h-5 w-5'/>
                :
                <FaMapMarkerAlt className='h-5 w-5'/>
                }
            </div>
            <h1 className='pl-2 font-semibold truncate'>{data.name!='' ? data.name : 'Untitled'}</h1>
        </div>
        :
        <div 
        className={`flex-shrink-0 ml-3 flex justify-between items-center h-12 max-w-[14rem] rounded-[2rem] border-2 border-gray1 hover:bg-gray1 transition duration-200 cursor-pointer ${!isEditing ? 'px-4' : 'pr-2'}`}
        >
            <div 
            className='h-12 w-12 mr-2 rounded-[2rem] hover:bg-gray2 transition duration-200 flex justify-center items-center'
            onClick={() => {
                setSavedLocations(savedLocations.filter((e) => JSON.stringify(e)!=JSON.stringify(data)))
            }}
            >
                <MdDelete
                    className='h-6 w-6'
                />
            </div>
            <h1 className='font-semibold truncate pr-4'>{data.name!='' ? data.name : 'Untitled'}</h1>
        </div>
    )
}

export default SavedLocationItem