import { useState, useEffect, useContext, useRef } from "react"
import { useLocation } from "react-router-dom"
import { MapContext } from "../../App"
import * as turf from '@turf/turf'
import axios from "axios"
import {IoMdInformationCircleOutline} from 'react-icons/io'

import RouteList from "../driver overlay components/RouteList"
import StatusPicker from "../driver overlay components/StatusPicker"
import LocateButton from "../driver overlay components/LocateButton"

const capitalizeFirstLetter = (str) => {
    if (!str) return str;
    return str.charAt(0).match(/[a-zA-Z]/) ? str.charAt(0).toUpperCase() + str.slice(1) : str;
};

const DriverOverlay = () => {

    const [isShowingInfo, setShowingInfo] = useState(false)

    const [message, setMessage] = useState(null)
    var messageTimeout

    const location = useLocation()
    const [isOnDriverPage, setOnDriverPage] = useState(false)
    useEffect(() => {
        setOnDriverPage(location.pathname=='/go')
    },[location.pathname])
    const isOnDriverPageRef = useRef(isOnDriverPage)
    useEffect(() => {isOnDriverPageRef.current=isOnDriverPage},[isOnDriverPage])

    const value = useContext(MapContext)
    const {isMapLoaded} = value
    const map = value.mapRef.current
    const {authenticationToken, isLoggedIn} = value

    //this useEffect listens to isOnDriverPage and toggles visibility of layers
    useEffect(() => {
        if(isMapLoaded){
            if(isOnDriverPage){
                if(map.getLayer('driver-live-location-layer')) map.setLayoutProperty('driver-live-location-layer','visibility','visible')
                if(map.getLayer('driver-remaining-route-layer')) map.setLayoutProperty('driver-remaining-route-layer','visibility','visible')
                if(map.getLayer('driver-passed-route-layer')) map.setLayoutProperty('driver-passed-route-layer','visibility','visible')
            }
            else{
                if(map.getLayer('driver-live-location-layer')) map.setLayoutProperty('driver-live-location-layer','visibility','none')
                if(map.getLayer('driver-remaining-route-layer')) map.setLayoutProperty('driver-remaining-route-layer','visibility','none')
                if(map.getLayer('driver-passed-route-layer')) map.setLayoutProperty('driver-passed-route-layer','visibility','none')
                routes.forEach((route) => {
                    const id = `driver-route-${route.route_id}-layer`
                    if(map.getLayer(id)) map.removeLayer(id)
                })
            }
        }
    },[isOnDriverPage])

    const {routes, setRoutes} = value
    const [chosenRoute, setChosenRoute] = useState(null)

    const [status, setStatus] = useState('inactive')

    const maxDistance = 0.5
    const [liveLocation, setLiveLocation] = useState(null)
    const [isSharingLiveLocation, setSharingLiveLocation] = useState(false)
    var liveLocationInterval
    const [isFollowingLiveLocation, setFollowingLiveLocation] = useState(false)
    const isFollowingLiveLocationRef = useRef(isFollowingLiveLocation)
    useEffect(() => {isFollowingLiveLocationRef.current=isFollowingLiveLocation},[isFollowingLiveLocation])

    //this useEffect listens to isSharingLiveLocation and starts/stops constant location update
    useEffect(() => {
        if(isSharingLiveLocation){
            liveLocationInterval = setInterval(() => {
                if(navigator.geolocation){
                    //geolocation is supported
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            //successfully got position
                            const { latitude, longitude } = position.coords;
                            setLiveLocation([longitude,latitude])
                        },
                        (error) => {
                            //couldn't get position
                            console.error('Error getting user location:', error);
                            setTimeout(() => {
                                setSharingLiveLocation(false); // Only set to false after a delay
                            }, 5000); // Retry after 5 seconds
                        }
                    )
                }
                else{
                    //geolocation is not supported
                    console.error("Geolocation is not supported")
                    setSharingLiveLocation(false)
                }
            },2000)//fetches live location every 2 seconds
        }
        else{
            setStatus('inactive')
            clearInterval(liveLocationInterval)
            setChosenRoute(null)
            setLiveLocation(null)
        }
    },[isSharingLiveLocation])

    //this useEffect listens to liveLocation and chosenRoute and updates sources and layers related to live location pulsing dot
    useEffect(() => {
        if(liveLocation && isSharingLiveLocation){
            if(map.getSource('driver-live-location')){
                //there's already a source for driver live location, so we just update
                if(chosenRoute){
                    //there's a chosen route, we have to project live location onto the route
                    //gets projection of live location onto route
                    const nearest= turf.nearestPointOnLine(chosenRoute.line,{type: "Point",coordinates: [liveLocation[0],liveLocation[1]]})  
                    const distance = nearest.properties.dist
                    if(distance<=maxDistance){
                        //driver is within the max distance from the road
                        map.getSource('driver-live-location').setData({
                            type: 'FeatureCollection',
                            features: [nearest]
                        })  
                    }  
                    else{
                        //driver is too far away
                        map.getSource('driver-live-location').setData({
                            type: 'FeatureCollection',
                            features: [{
                                type: 'Feature',
                                geometry: {type: 'Point', coordinates: liveLocation}
                            }]
                        })

                        setChosenRoute(null)
                        setStatus('unknown')
                        setMessage("You are too far away from the route. Status has been set to 'Unknown'")
                        //remove the message after 5 seconds
                        messageTimeout = setTimeout(() => {
                            setMessage(null)
                        },5000)
                    }
                }
                else{
                    setStatus('unknown')
                    //driver hasn't chosen a route yet, we show location as is
                    map.getSource('driver-live-location').setData({
                        type: 'FeatureCollection',
                        features: [{
                            type: 'Feature',
                            geometry: {type: 'Point', coordinates: liveLocation}
                        }]
                    })
                }
            }
            else{
                //there's no source for driver live location, need to add it
                setMessage("Your status will remain as 'Unknown' until you choose a route and status")
                //driver hasn't chosen a route yet so we dont project
                map.addSource('driver-live-location',{
                    type: 'geojson',
                    data: {
                        type: 'FeatureCollection',
                        features: [{
                            type: 'Feature',
                            geometry: {type: 'Point', coordinates: liveLocation}
                        }]
                    }
                })
                map.addLayer({
                    id: 'driver-live-location-layer',
                    type: 'symbol',
                    source: 'driver-live-location',
                    layout: {
                        'icon-image': 'pulsing-blue-dot'
                    }
                })
                //when driver drags the map, we stop following the dot
                map.on("drag",() => {
                    if(isOnDriverPageRef.current){
                        setFollowingLiveLocation(false)
                    }
                })
                //if driver presses on the pulsing blue dot, camera starts following it
                map.on("click","driver-live-location-layer",(e) => {
                    if(isOnDriverPageRef.current){
                        map.flyTo(e.features[0].geometry.coordinates)
                        setFollowingLiveLocation(true)
                    }
                })
                if(isOnDriverPageRef.current){
                    //fly to driver's live location if we just clicked the button
                    map.flyTo({center: liveLocation, zoom: 15})
                    setFollowingLiveLocation(true)
                }
                else{
                    //stop the pulsing dot from appearing until we go back to /go
                    map.setLayoutProperty('driver-live-location-layer','visibility','none')
                }
            }
            if(isFollowingLiveLocationRef.current && isOnDriverPageRef.current){
                map.panTo(map.getSource('driver-live-location')._data.features[0].geometry.coordinates)
            }
        }
        else{
            if(isMapLoaded){
                if(map.getLayer('driver-live-location-layer')) map.removeLayer('driver-live-location-layer')
                if(map.getSource('driver-live-location')) map.removeSource('driver-live-location')
            }
        }
    },[liveLocation, chosenRoute])
    //this useEffect also listens to liveLocation and chosenRoute and updates layers and sources related to remaining and passed route
    useEffect(() => {
        if(chosenRoute && liveLocation && turf.nearestPointOnLine(chosenRoute.line,{type: "Point",coordinates: [liveLocation[0],liveLocation[1]]}).properties.dist<=maxDistance){
            //driver is on route
            const nearest = turf.nearestPointOnLine(chosenRoute.line,{type: "Point",coordinates: [liveLocation[0],liveLocation[1]]})
            //const newCoordinates = [start.geometry.coordinates].concat(routeData.line.features[0].geometry.coordinates.slice(start.properties.index+1,end.properties.index+1),[end.geometry.coordinates])
            //divide the route into remaining portion and passed portion
            const remainingRouteCoordinates = [nearest.geometry.coordinates].concat(chosenRoute.line.features[0].geometry.coordinates.slice(nearest.properties.index+1,chosenRoute.line.features[0].geometry.coordinates.length))
            const passedRouteCoordinates = chosenRoute.line.features[0].geometry.coordinates.slice(0,nearest.properties.index+1).concat([nearest.geometry.coordinates])
            if(!map.getSource('driver-remaining-route')){
                //we need to add the sources and layers
                //source and layer for remaining route
                map.addSource('driver-remaining-route',{
                    type: 'geojson',
                    data:{
                        type: 'FeatureCollection',
                        features:[{type: 'Feature', properties:{}, geometry:{coordinates:remainingRouteCoordinates, type: 'LineString'}}]
                    }
                })
                map.addLayer({
                    id: 'driver-remaining-route-layer',
                    type: "line",
                    source: 'driver-remaining-route',
                    layout: {
                        "line-join": "round",
                        "line-cap": "round"
                    }, 
                    paint: {
                        "line-color": "#4050DE", // blue color
                        "line-width": 6 // thin line
                    }
                },"driver-live-location-layer")//so the dot is above the remaining line
                //source and layer for passed route
                map.addSource('driver-passed-route',{
                    type: 'geojson',
                    data:{
                        type: 'FeatureCollection',
                        features:[{type: 'Feature', properties:{}, geometry:{coordinates:passedRouteCoordinates, type: 'LineString'}}]
                    }
                })
                map.addLayer({
                    id: 'driver-passed-route-layer',
                    type: "line",
                    source: 'driver-passed-route',
                    layout: {
                        "line-join": "round",
                        "line-cap": "round"
                    }, 
                    paint: {
                        "line-color": "#888888", // gray color
                        "line-width": 4 ,// thin line
                    }
                },'driver-live-location-layer')//so the dot is above the passed line
                
                //driver just added a route, prompt him to pick a status
                clearTimeout(messageTimeout)
                setMessage("Please pick your current status from bottom left menu, your status will remain as 'Unknown' until then")
            }
            else{
                //source is already there just need to update it
                map.getSource('driver-remaining-route').setData({
                    type: 'FeatureCollection',
                    features:[{type: 'Feature', properties:{}, geometry:{coordinates:remainingRouteCoordinates, type: 'LineString'}}]
                })
                map.getSource('driver-passed-route').setData({
                    type: 'FeatureCollection',
                    features:[{type: 'Feature', properties:{}, geometry:{coordinates:passedRouteCoordinates, type: 'LineString'}}]
                })
            }
        }
        else{
            if(isMapLoaded){
                if(map.getLayer('driver-remaining-route-layer')) map.removeLayer('driver-remaining-route-layer')
                if(map.getSource('driver-remaining-route')) map.removeSource('driver-remaining-route')
                if(map.getLayer('driver-passed-route-layer')) map.removeLayer('driver-passed-route-layer')
                if(map.getSource('driver-passed-route')) map.removeSource('driver-passed-route')
            }
        }
    },[liveLocation, chosenRoute])

    //this useEffect listens to chosenRoute and determines if driver is on a route at the moment, if not it resets states
    useEffect(() => {
        if(chosenRoute){
            //driver is on route
        }
        else{
            //driver isnt on route
            //status is now unknown
            if(status!='inactive'){
                setStatus('unknown')
                
            }
            //remove any message that was there
            messageTimeout = setTimeout(() => {
                setMessage(null)
            },5000)
        }
    },[chosenRoute, status])

    //handles click of locate button in bottom left corner
    const handleLocateClick = () => {
        if(isMapLoaded){
            setSharingLiveLocation(!isSharingLiveLocation)
        }
    }

    //handles click of route item
    const handleRouteItemClick = (route) => {
        if(isSharingLiveLocation && liveLocation && (!chosenRoute || chosenRoute.route_id!=route.route_id)){
            //driver is sharing their location
            const distance = turf.nearestPointOnLine(route.line,{type: "Point",coordinates: [liveLocation[0],liveLocation[1]]}).properties.dist
            if(distance<=maxDistance){
                //driver is within the max distance from the road
                setChosenRoute(route)
                //push the chosen route to the top of the list
                setRoutes([route].concat(routes.filter((e) => e!=route)))
            }
            else{
                //driver is too far away
                setMessage('You are too far away from the route')
                //remove the message after 5 seconds
                messageTimeout = setTimeout(() => {
                    setMessage(null)
                },5000)
            }
        }
        else if(!isSharingLiveLocation){
            //driver isn't sharing their location, they should
            setMessage('You should share your location by clicking on the bottom right button before picking a route')
            //remove the message after 5 seconds
            messageTimeout = setTimeout(() => {
                setMessage(null)
            },5000)
        }
    }

    //handles choosing of a status in the bottom left corner status picker
    const handleStatusClick = (option) => {
        if(isSharingLiveLocation && chosenRoute){
            setStatus(option)
            clearTimeout(messageTimeout)
            //remove the message after 5 seconds
            setMessage(`Status has been set to ${capitalizeFirstLetter(option)}`)
            messageTimeout = setTimeout(() => {
                setMessage(null)
            },5000)
        }
        if(!isSharingLiveLocation && !chosenRoute){
            setMessage("You must share your location and choose a route to pick a status")
            //remove the message after 5 seconds
            messageTimeout = setTimeout(() => {
                setMessage(null)
            },5000)
        }
        else if(!chosenRoute){
            setMessage("You must choose a route to pick a status")
            //remove the message after 5 seconds
            messageTimeout = setTimeout(() => {
                setMessage(null)
            },5000)
        }
    }

    const accessToken = localStorage.getItem('authentication-token') ? localStorage.getItem('authentication-token') : authenticationToken
    //putting location to api
    const putLocation = async () => {
        await axios({
            method: 'put',
            url:'/api/vehicle_location',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            data: {
                longitude: liveLocation[0],
                latitude: liveLocation[1]
            }
        })
        .then((res) => {

        })
    }
    //puts live location to api everytime it changes
    useEffect(() => {
        if(liveLocation){
            putLocation()
        }
    },[liveLocation])

    //putting status to API
    const putStatus = async () => {
        await axios({
            method: 'put',
            url:`/api/vehicle_status?new_status=${status}`,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            }
        })
        .then((res) => {
            if(res.status==200){

            }
        })
    }
    //puts status everytime it changes
    useEffect(() => {
        putStatus()
    },[status])
    
    const putCurrentRoute = async () => {
        await axios({
            method: 'put',
            url:`/api/active_route?new_active_route=${chosenRoute.route_id}`,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            }
        })
        .then((res) => {

        })
    }
    useEffect(() => {
        if(chosenRoute){
            putCurrentRoute()
        }
    },[chosenRoute])

    return (
        isOnDriverPage &&
        (isShowingInfo ?
        <div className='absolute h-screen w-full z-40 bg-opacity-20 backdrop-blur-sm flex justify-center items-center bg-black'>
            <div className="flex justify-center items-center w-full h-full p-3">
                <div className="p-6 bg-white rounded-xl shadow-md w-full max-w-[30rem]">
                    <h1 className='font-bold'>1. Start sharing your location from the bottom right button</h1>
                    <h1 className='font-bold pb-3'>Your status will be displayed as Unknown to passengers for now</h1>
                    <h1 className='font-bold pb-3'>2. Choose the route that you'll be operating on (it has to be close to your current location) from the top route list</h1>
                    <h1 className='font-bold pb-3'>3. Pick your status from the bottom right section:</h1>
                    <h1 className='font-semibold pb-1'><span className='rounded-lg bg-active-green py-1 px-2 text-white text-base font-medium'>Active</span> means you are driving and actively looking for passengers</h1>
                    <h1 className='font-semibold pb-1'><span className='rounded-lg bg-waiting-yellow py-1 px-2 text-white text-base font-medium'>Waiting</span> means you are stationary and accepting passengers</h1>
                    <h1 className='font-semibold pb-6'><span className='rounded-lg bg-unavailable-red py-1 px-2 text-white text-base font-medium'>Unavailable</span> means you are not in a position to accept passengers (driving on the highway, vehicle is full... )</h1>
                    <div className='flex justify-center items-center h-10'>
                        <div 
                        className='border-2 border-gray1 hover:bg-gray1 transition duration-200 rounded-xl flex justify-center items-center cursor-pointer py-2'
                        onClick={() => setShowingInfo(false)}
                        >
                            <h1 className='px-6 font-semibold'>Understood</h1>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        :
        <div className='absolute z-10 pointer-events-none w-full h-screen flex flex-col justify-between p-3 border-b-[64px] md:border-b-[56px]'>
            <div className='flex justify-center md:justify-normal w-full'>
                <div className='flex-col items-center max-w-96 w-full'>
                    <RouteList
                    routes={routes}
                    chosenRoute={chosenRoute}
                    setChosenRoute={setChosenRoute}
                    isSharingLiveLocation={isSharingLiveLocation}
                    handleRouteItemClick={handleRouteItemClick}
                    />
                    <div 
                    className={`bg-blue3 text-white transition duration-500 ease-in-out mt-3 rounded-xl shadow-md h-14 px-4 w-full max-w-96 flex justify-center items-center text-sm ${message ? 'opacity-90 hover:opacity-100 pointer-events-auto cursor-pointer' : 'opacity-0 pointer-events-none cursor-auto'}`}
                    onClick={() => {
                        setMessage(null)
                        clearTimeout(messageTimeout)
                    }}
                    >
                    {message}
                    </div>
                </div>  
            </div>
            
            <div className='flex justify-between items-end w-full'>
                <StatusPicker
                status={status}
                handleStatusClick={handleStatusClick}
                />
                <div className='flex flex-col items-end'>
                    <div 
                    className='mb-3 pointer-events-auto cursor-pointer h-8 w-8 flex items-center justify-center bg-white rounded-xl opacity-90 hover:opacity-100 shadow-md'
                    onClick={() => setShowingInfo(true)}
                    >
                        <IoMdInformationCircleOutline className='h-6 w-6 text-gray2'/>
                    </div>
                    <LocateButton
                    handleLocateClick={handleLocateClick}
                    isSharingLiveLocation={isSharingLiveLocation}
                    />
                </div>
                
            </div>
        </div>
        )
    )
}

export default DriverOverlay