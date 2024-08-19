import React, {useRef,useState,useEffect} from 'react'
import axios from 'axios'
import mapboxgl from 'mapbox-gl';
import './App.css'
import {Navigate, Route, createBrowserRouter, createRoutesFromElements, RouterProvider, useLocation} from 'react-router-dom';
import Layout from './components/Layout';
import BussesPage from './components/pages/BussesPage';
import SettingsPage from './components/pages/SettingsPage';
import SignInLayout from './components/SignInLayout'
import SignInPage from './components/pages/SignInPage';
import CreatePassengerAccountPage from './components/pages/CreatePassengerAccountPage';
import PageNotFound from './components/pages/PageNotFound'
import RouteInfoPage from './components/busses page components/RouteInfoPage';
import BusInfoPage from './components/busses page components/BusInfoPage';
import Map from './components/Map';
import CreateDriverAccountPage from './components/pages/CreateDriverAccountPage';
import AccountInfoPage from './components/pages/AccountInfoPage';
import ContributePage from './components/pages/ContributePage';
import FeedbackForm from './components/pages/FeedbackForm';
import AboutUsPage from './components/pages/AboutUsPage';

export const MapContext= React.createContext()
//will provide map reference... to all child components

//fetches search data, takes in query, data setter and loading setter
export const fetchSearchData = async (query, setSearchData, setSearchLoading) => {
  try{
    //link automatically fixes symbols, whitespaces etc...
    await axios.get(`https://photon.komoot.io/api/?q=${query}&lat=33.8338&lon=35.8015&zoom=8`,{
      headers:{
        'Content-Type':'application/json'
      }
    }).then( res => {
      //filter results, only show those with countrycode LB and not localities (because they can be found as city or district)
      setSearchData(res.data.features.filter((element)=>{return element.properties.countrycode=='LB' && element.properties.type!='locality'}))
      setSearchLoading(false)
      }
    )
  }
  catch (error){
    setSearchLoading(false)
  }
}

function App() {

  //states related to user
  const [authenticationToken, setAuthenticationToken] = useState('')
  const [isLoggedIn, setLoggedIn] = useState(false)
  const [userType, setUserType] = useState('passenger')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [email, setEmail] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')

  const [savedLocations, setSavedLocations] = useState([])
  const [savedVehicles, setSavedVehicles] = useState([])
  const [savedRoutes, setSavedRoutes] = useState([])

  //driver specific states
  const [vehicleType, setVehicleType] = useState('')
  const [licensePlate, setLicensePlate] = useState('')
  const [vehicleBrand, setVehicleBrand] = useState('')
  const [vehicleModel, setVehicleModel] = useState('')
  const [vehicleColor, setVehicleColor] = useState('')
  const [routes, setRoutes] = useState([])

  const mapRef = useRef()
  //will use mapRef.current as a reference to the map, can be used in any component
  const [isMapLoaded,setMapLoaded] = useState(false)
  const [isOnMapPage, setOnMapPage] = useState(false)
  useEffect(() => {
    setOnMapPage(window.location.href.endsWith('/map'))
  },[window.location.href])

  var marker = new mapboxgl.Marker({
    color: '#4050DE',
    scale: 0.7
  }) 
  marker._element.id='marker'

  var startMarker = new mapboxgl.Marker({
    color: '#4050DE',
    scale: 0.7
  })
  startMarker._element.id='start-marker'

  var destinationMarker = new mapboxgl.Marker({
    color: '#4050DE',
    scale: 0.7
  })
  destinationMarker._element.id='destination-marker'

  const [busData, setBusData] = useState(null)

  const [chosenBusIds,setChosenBusIds] = useState(null)

  const [lookingAtBus, setLookingAtBus] = useState(false)
  const [singleChosenBusId, setSingleChosenBusId] = useState(null)
  const [chosenBusData, setChosenBusData] = useState(null)
  const [isChosenBusDataLoading, setChosenBusDataLoading] = useState(false)

  const [chosenRoute, setChosenRoute] = useState(null)
  const [chosenRouteIntervalId, setChosenRouteIntervalId] = useState(null)
  const [isChosenRouteLoading, setChosenRouteLoading] = useState(false)

  const [lng, setLng] = useState(35.8015);
  const [lat, setLat] = useState(33.8338);
  const [zoom, setZoom] = useState(7.67);

  //fetches data abt specific bus without token (to be changed) (has been changed)
  const fetchChosenBusData = async (id) => {
    //new version
    await axios.get(`/api/vehicle/${id}`,{
      headers:{
        'Content-Type':'application/json'
      }
    })
    .then((res) => {
        if(res.status==200){
          if(res.data.content.status!='inactive'){
            setBusData(busData.filter((e) => e.properties.id!=res.data.content.id).concat([{
              properties: {
                id: res.data.content.id,
                status: res.data.content.status
              },
              geometry: {
                coordinates: res.data.content.coordinates,
                type:'Point'
              }
            }]))
          }   
          setChosenBusData(res.data.content)
          setChosenBusDataLoading(false)
        }
      }
    ).catch((e) => {
      setSingleChosenBusId(null)
      setChosenBusDataLoading(false)
    })
  }

  //fetches data abt specific route (to be changed) (has been changed)
  const fetchRouteData = async (route_id) => {
    //new version
    await axios.get(`/api/route/${route_id}`,{
      headers:{
        'Content-Type':'application/json'
      }
    })
    .then((res) => {
        if(res.status==200){
          setChosenRoute(res.data.route_data)
          setChosenRouteLoading(false)
        }
      }
    ).catch((e) => {
      setChosenRoute(null)
      if(chosenRouteIntervalId){
        clearInterval(chosenRouteIntervalId)
      }
    })
  }

  const checkToken = async (accessToken) => {
    await axios({
      method: 'get',
      url: `/api/check_token?token=${accessToken}`,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then((res) => {
      if(res.status==200){
        if(res.data.is_valid){
          setAuthenticationToken(accessToken)
          setLoggedIn(true)
        }
        else{
          localStorage.setItem('authentication-token','')
        }
      }
    })
    .catch((e) => {
      localStorage.setItem('authentication-token','')
    })
  }

  //runs on render, adds history items and authentication token to local storage
  useEffect(() => {
    //can only have strings as values
    if(!localStorage.getItem('routes-history') || localStorage.getItem('routes-history').length==0) localStorage.setItem('routes-history',JSON.stringify([]))
    if(!localStorage.getItem('busses-history') || localStorage.getItem('busses-history').length==0) localStorage.setItem('busses-history',JSON.stringify([]))
    if(!localStorage.getItem('authentication-token') || localStorage.getItem('authentication-token').length==0) localStorage.setItem('authentication-token','')
    const accessToken = localStorage.getItem('authentication-token')
    if(accessToken!=''){
      checkToken(accessToken)
    }
    
  },[])

  const fetchUserInfo = async () => {
    await axios({
      method: 'get',
      url: '/api/account_info',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authenticationToken}`
      }
    })
    .then((res) => {
      if(res.status==200){
        if(res.data.account_type=='driver'){
          setUserType('driver')
          setRoutes(res.data.route_list)
          setLicensePlate(res.data.license_plate)
          setVehicleBrand(res.data.brand)
          setVehicleModel(res.data.model)
          setVehicleColor(res.data.color)
        }
        else{
          setUserType('passenger')
        }
        setFirstName(res.data.first_name)
        setLastName(res.data.last_name)
        setDateOfBirth(res.data.date_of_birth)
        setEmail(res.data.email)
        setPhoneNumber(res.data.phone_number)
        setSavedLocations(res.data.saved_locations.map((e) => {return {name: e.name, coordinates: [e.longitude, e.latitude], icon: e.icon}}))
        setSavedRoutes(res.data.saved_routes)
        setSavedVehicles(res.data.saved_vehicles)
      }
    })
    .catch()
  }
  //this useEffect listens to changes to authenticationToken and updates info states
  useEffect(() => {
    if(authenticationToken!=''){
      fetchUserInfo()
    }
  },[authenticationToken])

  const putSavedLocations = async () => {
    await axios({
      method: 'put',
      url: '/api/saved_locations',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authenticationToken}`
      },
      data: {
        saved_locations: savedLocations.map((e) => {return {name: e.name, longitude: e.coordinates[0], latitude: e.coordinates[1], icon: e.icon}})
      }
    })
    .catch()
  }
  //this useEffect listens to changes to savedLocations and puts to API
  useEffect(() => {
    if(isLoggedIn && authenticationToken!=''){
      putSavedLocations()
    }
  },[savedLocations])

  const putSavedVehicles = async () => {
    await axios({
      method: 'put',
      url: '/api/saved_vehicles',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authenticationToken}`
      },
      data: {
        saved_vehicles: savedVehicles.map((e) => {return {nickname: e.nickname, vehicle_id: e.id}})
      }
    })
    .catch()
  }
  //this useEffect listens to changes to savedVehicles and puts to API
  useEffect(() => {
    if(isLoggedIn && authenticationToken!=''){
      putSavedVehicles()
    }
  },[savedVehicles])

  const putSavedRoutes = async () => {
    
    await axios({
      method: 'put',
      url: '/api/saved_routes',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authenticationToken}`
      },
      data: {
        saved_routes: savedRoutes.map((e) => e.route_id)
      }
    })
    .catch()
  }
  //this useEffect listens to changes to savedRoutes and puts to API
  useEffect(() => {
    if(isLoggedIn && authenticationToken!=''){
      putSavedRoutes()
    }
  },[savedRoutes])

  const router = createBrowserRouter(createRoutesFromElements(
    <>
      <Route path='/' element={<Layout/>}>
        <Route index element={<Navigate to="/map" replace />}/>
        <Route path='/go' element={<></>}/>
        <Route path="/map" element={<></>}/>
        <Route path='/search' element={<BussesPage/>}>
          <Route path='/search' element={<div className='hidden md:block w-full backdrop-blur-sm'></div>}/>
          <Route path='/search/route/:id' element={<RouteInfoPage/>}/>
          <Route path='/search/bus/:id' element={<BusInfoPage/>}/>
        </Route>
        <Route path='/saved' element={<></>}/>
        <Route path="/settings" element={<SettingsPage/>}>
          <Route path='/settings' element={<div className='hidden md:block w-full backdrop-blur-sm'></div>}/>
          <Route path='/settings/account' element={<AccountInfoPage/>}/>
          <Route path='/settings/contribute' element={<ContributePage/>}/>
          <Route path='/settings/about-us' element={<AboutUsPage/>}/>
        </Route>
      </Route>
      <Route path='/sign-in' element={<SignInLayout/>}>
        <Route path='/sign-in' element={<SignInPage/>}/>
        <Route path='/sign-in/create-passenger-account' element={<CreatePassengerAccountPage/>}/>
        <Route path='/sign-in/create-driver-account' element={<CreateDriverAccountPage/>}/>
      </Route>
      <Route path='/feedback' element={<FeedbackForm/>}/>
      <Route path='*' element={<PageNotFound/>}/> 
    </>
  ))

  return (
    <>
      <MapContext.Provider value={{
        //user stuff
        authenticationToken, setAuthenticationToken,
        isLoggedIn, setLoggedIn,
        userType, setUserType, 
        dateOfBirth, setDateOfBirth,
        firstName, setFirstName,
        lastName, setLastName,
        email, setEmail,
        phoneNumber, setPhoneNumber,

        savedLocations, setSavedLocations,
        savedVehicles, setSavedVehicles,
        savedRoutes, setSavedRoutes,

        //driver specific stuff
        vehicleType, setVehicleType,
        licensePlate, setLicensePlate,
        vehicleBrand, setVehicleBrand,
        vehicleModel, setVehicleModel,
        vehicleColor, setVehicleColor,
        routes, setRoutes, 
        //map stuff
        mapRef,
        isMapLoaded,setMapLoaded,
        isOnMapPage, setOnMapPage,
        marker, startMarker, destinationMarker,
        lng,
        lat,
        zoom,
        fetchChosenBusData, fetchRouteData,
        lookingAtBus, setLookingAtBus,
        chosenBusData, setChosenBusData,
        busData, setBusData,
        isChosenBusDataLoading, setChosenBusDataLoading,
        chosenBusIds, setChosenBusIds,
        singleChosenBusId, setSingleChosenBusId,
        chosenRoute, setChosenRoute,
        chosenRouteIntervalId, setChosenRouteIntervalId,
        isChosenRouteLoading, setChosenRouteLoading
      }}>
        <RouterProvider router={router} className='router'/>
        <Map/>
      </MapContext.Provider>

    </>
  )
}

export default App
