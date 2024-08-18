import {useState, useEffect, useContext, useRef} from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { FaMapMarkerAlt, FaGraduationCap, FaBus, FaBriefcase, FaBusAlt } from 'react-icons/fa'
import { FaHouse, FaPerson } from 'react-icons/fa6'
import { MdAdd, MdEdit } from 'react-icons/md'
import {IoMdClose} from 'react-icons/io'
import { MapContext } from '../../App'
import mapboxgl from 'mapbox-gl'
import SavedLocationItem from '../saved components/SavedLocationItem'
import SavedVehicleItem from '../saved components/SavedVehicleItem'
import { PiPathBold} from "react-icons/pi"
import SavedRouteItem from '../saved components/SavedRouteItem'
import NeedToLoginPrompt from '../NeedToLoginPrompt'

const SavedPage = () => {

    const location = useLocation()
    const [isOnSaved, setOnSaved] = useState(false)
    useEffect(() => {setOnSaved(location.pathname=='/saved')},[location.pathname])
    useEffect(() => {
        isOnSavedRef.current=isOnSaved
        if(!isOnSaved){
            setOnMap(false)
            setEditingLocations(false)
            setEditingVehicles(false)
            setEditingRoutes(false)
        }
    },[isOnSaved])
    const isOnSavedRef = useRef(isOnSaved)

    const value = useContext(MapContext)
    const {isMapLoaded, isLoggedIn} = value
    const map=value.mapRef.current
    const {savedLocations, setSavedLocations} = value
    const {savedVehicles, setSavedVehicles} = value
    const {savedRoutes, setSavedRoutes} = value
    
    const [isOnMap, setOnMap] = useState(false) 

    const [locationToSave, setLocationToSave] = useState(null)
    const [locationName, setLocationName] = useState('')
    const [locationIcon, setLocationIcon] = useState('marker')

    const locationMarker = new mapboxgl.Marker({
        color: '#4050DE',
        scale: 0.7
    })
    locationMarker._element.id='location-marker'
    const removeLocationMarker = () => {
        if(document.getElementById('location-marker'))document.getElementById('location-marker').remove()
    }
    const resetStates = () => {
        removeLocationMarker()
        setLocationToSave(null)
        setLocationName('')
        setLocationIcon('marker')
    }
    locationMarker._element.addEventListener('click', (e) => {
        if(!isOnSaved) return;
        e.stopPropagation()
        resetStates()
    })

    //this use useEffect listens to isOnMap and resets states
    useEffect(() => {
        resetStates()
    },[isOnMap])

    var clickTimeout
    //this useEffect listens to isMapLoaded and adds event listeners
    useEffect(() => {
        if(isMapLoaded){
            map.on('click', e => {
                if(!isOnSavedRef.current) return;
                clickTimeout = setTimeout(() => {
                    resetStates()
                    locationMarker.remove()
                    locationMarker.setLngLat(e.lngLat).addTo(map)
                    setLocationToSave([e.lngLat.lng, e.lngLat.lat])
                    map.flyTo({center: e.lngLat, zoom: Math.max(13, map.getZoom())})
                },350)
        })
            map.on('zoom',() => {
                if(!isOnSavedRef.current) return;
                if(clickTimeout){
                    clearTimeout(clickTimeout)
                }
            })
        }
    },[isMapLoaded])

    //this useEffect listens to isOnSaved and toggles visibility of location marker
    useEffect(() => {
        if(isMapLoaded){
            if(isOnSaved){
                if(document.getElementById('location-marker')) document.getElementById('location-marker').style.visibility='visible'
            }
            else{
                if(document.getElementById('location-marker')) document.getElementById('location-marker').style.visibility='hidden'
            }
        }
    },[isOnSaved])

    const handleAddLocation = () => {
        setSavedLocations(savedLocations.concat([{
            coordinates: locationToSave,
            name: locationName,
            icon: locationIcon
        }]))
        setOnMap(false)
    }

    const [isEditingLocations, setEditingLocations] = useState(false)
    const [isEditingVehicles, setEditingVehicles] = useState(false)
    const [isEditingRoutes, setEditingRoutes] =useState(false)

    const navigate = useNavigate()

    return (
        isOnSaved &&
        (!isLoggedIn ?
        <div className='absolute h-screen w-full z-40 bg-opacity-20 backdrop-blur-sm flex justify-center items-center bg-black'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md'>
                <div className='w-full h-32 p-6 flex justify-center items-center'>
                    <h1 className='font-medium'>You need to be logged in to save locations, vehicles and routes</h1>
                </div>
                <div className='px-6 pb-6 flex items-center justify-between'>
                    <div 
                    className='mr-1.5 h-10 w-full bg-blue3 rounded-xl cursor-pointer flex justify-center items-center'
                    onClick={() => {navigate('/settings')}}
                    >
                        <h1 className='text-white'>Go to Settings</h1>
                    </div>
                    <div 
                    className='ml-1.5 h-10 w-full border-2 border-gray1 rounded-xl hover:bg-gray1 transition duration-200 cursor-pointer flex justify-center items-center'
                    onClick={() => {
                        navigate('/map')
                    }
                    }
                    >
                        <h1>Go to Map</h1>
                    </div>
                </div>
            </div>
        </div>
        :
        isOnMap ?
        <div className='absolute z-10 pointer-events-none w-full h-screen flex flex-col justify-between p-3 border-b-[64px] md:border-b-[56px]'>
            <div className="flex flex-col justify-center items-center">
                <div
                className='mb-3 pointer-events-auto w-full max-w-96 flex justify-center items-center h-14 lg:h-12 rounded-xl bg-white opacity-90 hover:opacity-100 shadow-md cursor-pointer transition duration-200'
                onClick={() => setOnMap(false)}
                >
                    <h1 className='text-gray4 text-[18px] lg:text-[16px]'>Click here to go back</h1>
                </div>
                <div
                className='text-sm text-white mb-3 pointer-events-auto w-full max-w-96 flex justify-center items-center h-8 lg:h-7 rounded-xl bg-blue3 opacity-90 hover:opacity-100 shadow-md'
                >
                    <h1>{locationToSave ? 'Name this location and pick one of the icons below' : 'Click anywhere on the map to choose a location'}</h1>
                </div>
            </div>
            {locationToSave &&
            <div className='flex justify-center'>
                <div className='pointer-events-auto bg-white w-full max-w-96 rounded-xl shadow-md p-3'>
                    <div className='flex justify-center'>
                        <h1 className='font-semibold'>Saving new location</h1>
                    </div>
                    <input
                    value={locationName}
                    className="w-full my-3 px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                    placeholder='Name this location'
                    onChange={(e) => setLocationName(e.target.value)}
                    />
                    <div className='flex items-center justify-between mb-3'>
                        <div 
                        className={`h-10 w-10 flex justify-center items-center rounded-[2rem] ${locationIcon=='marker' ? 'bg-gray2' : 'border-2 border-gray1 hover:bg-gray1'} transition duration-200 cursor-pointer`}
                        onClick={() => setLocationIcon('marker')}
                        >
                            <FaMapMarkerAlt/>
                        </div>
                        <div 
                        className={`h-10 w-10 flex justify-center items-center rounded-[2rem] ${locationIcon=='home' ? 'bg-gray2' : 'border-2 border-gray1 hover:bg-gray1'} transition duration-200 cursor-pointer`}
                        onClick={() => setLocationIcon('home')}
                        >
                            <FaHouse/>
                        </div>
                        <div 
                        className={`h-10 w-10 flex justify-center items-center rounded-[2rem] ${locationIcon=='work' ? 'bg-gray2' : 'border-2 border-gray1 hover:bg-gray1'} transition duration-200 cursor-pointer`}
                        onClick={() => setLocationIcon('work')}
                        >
                            <FaBriefcase/>
                        </div>
                        <div 
                        className={`h-10 w-10 flex justify-center items-center rounded-[2rem] ${locationIcon=='school' ? 'bg-gray2' : 'border-2 border-gray1 hover:bg-gray1'} transition duration-200 cursor-pointer`}
                        onClick={() => setLocationIcon('school')}
                        >
                            <FaGraduationCap/>
                        </div>
                        <div 
                        className={`h-10 w-10 flex justify-center items-center rounded-[2rem] ${locationIcon=='person' ? 'bg-gray2' : 'border-2 border-gray1 hover:bg-gray1'} transition duration-200 cursor-pointer`}
                        onClick={() => setLocationIcon('person')}
                        >
                            <FaPerson/>
                        </div>
                        <div 
                        className={`h-10 w-10 flex justify-center items-center rounded-[2rem] ${locationIcon=='bus' ? 'bg-gray2' : 'border-2 border-gray1 hover:bg-gray1'} transition duration-200 cursor-pointer`}
                        onClick={() => setLocationIcon('bus')}
                        >
                            <FaBus/>
                        </div>
                    </div>
                    <div 
                    className='h-10 flex justify-center items-center bg-blue3 hover:bg-blue4 transition duration-200 rounded-xl cursor-pointer'
                    onClick={handleAddLocation}
                    >
                        <h1 className='text-white'>Add Location</h1>
                    </div>
                </div>
            </div>
            }
        </div>
        :
        <div className='absolute w-full h-full backdrop-blur-sm p-3 border-b-[64px] md:border-b-[56px]'>
            <div className='bg-white h-full w-full max-w-xl rounded-xl flex flex-col'>
                <div className='px-6 py-4 border-b-2 border-gray2'>     
                    <h1 className='text-xl font-bold'>Saved</h1>
                </div>
                <div className='p-3 pb-0 border-b-2 border-gray2'>
                    <div className='flex justify-between'>
                        <div className='flex items-center pb-3'>
                            <FaMapMarkerAlt className='mr-2'/>
                            <h1 className='text-lg font-bold'>Locations</h1>
                        </div>
                        <div 
                        className='pt-1 cursor-pointer'
                        onClick={() => setEditingLocations(!isEditingLocations)}
                        >
                            {isEditingLocations ?
                            <IoMdClose className='h-5 w-5'/>
                            :
                            <MdEdit className='h-5 w-5'/>
                            }
                        </div>
                    </div>
                    
                    <div className='flex items-center overflow-x-scroll whitespace-nowrap'>
                        {!isEditingLocations ?
                        <div 
                        className='flex-shrink-0 flex justify-center items-center h-12 w-12 rounded-[2rem] bg-blue3 hover:bg-blue4 text-white transition duration-200 cursor-pointer'
                        onClick={() => setOnMap(true)}
                        >
                            <MdAdd className='h-8 w-8'/>
                        </div>
                        : 
                        savedLocations.length==0 &&
                        <div className='h-12 w-full flex justify-center items-center'>
                            <h1 className='text-gray4'>There are no saved locations</h1>
                        </div>
                        }
                        {
                        savedLocations.map((e,i) => <SavedLocationItem key={i} data={e} isEditing={isEditingLocations}/>)
                        }
                    </div>
                </div>
                <div className='p-3 pb-0 border-b-2 border-gray2'>
                    <div className='flex justify-between'>
                        <div className='flex items-center pb-3'>
                            <FaBusAlt className='mr-2'/>
                            <h1 className='text-lg font-bold'>Vehicles</h1>
                        </div>
                        <div 
                        className='pt-1 cursor-pointer'
                        onClick={() => setEditingVehicles(!isEditingVehicles)}
                        >
                            {isEditingVehicles ?
                            <IoMdClose className='h-5 w-5'/>
                            :
                            <MdEdit className='h-5 w-5'/>
                            }
                        </div>
                    </div>
                    
                    <div className='flex items-center overflow-x-scroll whitespace-nowrap'>
                        {
                        savedVehicles.length==0 ?
                        <div className='h-12 w-full flex justify-center items-center'>
                            <h1 className='text-gray4'>There are no vehicles saved</h1>
                        </div>
                        :
                        savedVehicles.map((e,i) => <SavedVehicleItem key={i} vehicleItem={e} isEditing={isEditingVehicles}/>)}
                    </div>
                </div>
                <div className="flex justify-between p-3">
                    <div className='flex items-center'>
                        <PiPathBold className='h-5 w-5 mr-2'/>
                        <h1 className='text-lg font-bold'>Routes</h1>
                    </div>
                    <div 
                    className='pt-1 cursor-pointer'
                    onClick={() => setEditingRoutes(!isEditingRoutes)}
                    >
                        {isEditingRoutes ?
                        <IoMdClose className='h-5 w-5'/>
                        :
                        <MdEdit className='h-5 w-5'/>
                        }
                    </div>
                </div>
                
                {savedRoutes.length==0
                ?
                <div className='h-full w-full flex justify-center items-center'>
                    <h1 className='text-gray4'>There are no routes saved</h1>
                </div>
                :
                <div className='w-full scrollable h-full pb-3 overflow-auto'>
                    {savedRoutes.map((e,i) => <SavedRouteItem key={i} routeData={e} isEditing={isEditingRoutes}/>)}
                </div>
                }
            </div>
        </div>
        
        )
    )
}

export default SavedPage