import {useState,useEffect,useContext,useRef} from 'react'
import { useLocation } from 'react-router-dom'
import {MapContext} from '../../App'
import axios from 'axios'
import * as turf from '@turf/turf'
import LocationSearchBar from '../overlay components/LocationSearchBar'
import DirectionsSearch from '../overlay components/DirectionsSearch'
import ShowBussesButton from '../overlay components/ShowBussesButton'
import LocateButton from '../overlay components/LocateButton'
import NearbyRoutesButton from '../overlay components/NearbyRoutesButton'
import BusDataCard from '../overlay components/BusDataCard'
import ExpectedTimeCard from '../overlay components/ExpectedTimeCard'
import NearbyRoutesResults from '../overlay components/NearbyRoutesResults'
import ExpectedTimesCard from '../overlay components/ExpectedTimesCard'
import BussesOnRouteCard from '../overlay components/BussesOnRouteCard'
import DirectionsResults from '../overlay components/DirectionsResults'
import BusStopDataCard from '../overlay components/BusStopDataCard'
import NeedToLoginPrompt from '../NeedToLoginPrompt'
import GiveNicknamePrompt from '../GiveNicknamePrompt'

const MapOverlay = () => {

  const value = useContext(MapContext)

  const [needsToLogin, setNeedsToLogin] = useState(false)
  const [message, setMessage] = useState('')
  const [needsToGiveNickname, setNeedsToGiveNickname] = useState(false)

  const location = useLocation()
  const {isOnMapPage, setOnMapPage} = value
  useEffect(() => {
    setOnMapPage(location.pathname=='/map')
  },[location.pathname])
  const isOnMapPageRef = useRef(isOnMapPage)
  useEffect(() => {isOnMapPageRef.current=isOnMapPage},[isOnMapPage])

  const map = value.mapRef.current
  const {isMapLoaded, fetchChosenBusData, marker, startMarker, destinationMarker, fetchRouteData} = value

  let clickTimeout;

  const [isUsingDirections, setUsingDirections] = useState(false)

  const [startingPoint, setStartingPoint] = useState(null)
  const [destination, setDestination] = useState(null)
  const startingPointRef = useRef(startingPoint); 
  const destinationRef = useRef(destination);
  const [directionsResults, setDirectionsResults] = useState(null)
  const [areDirectionsResultsLoading, setDirectionsResultsLoading] = useState(false)

  const [isSharingLocation,setSharingLocation] = useState(false)
  const [liveLocation, setLiveLocation] = useState(null)
  const liveLocationRef = useRef(liveLocation)
  useEffect(() => {liveLocationRef.current=liveLocation},[liveLocation])
  const [locationIntervalId, setLocationIntervalId] = useState(null);

  const [isShowingBusses, setShowingBusses] = useState(false)
  const {busData, setBusData} = value
  const [bussesIntervalId, setBussesInvervalId] = useState(null)

  const {chosenBusIds,setChosenBusIds} = value

  const {lookingAtBus, setLookingAtBus} = value
  const {chosenBusData, setChosenBusData} = value
  const [chosenBusIntervalId, setChosenBusIntervalId] = useState(null)
  const {isChosenBusDataLoading, setChosenBusDataLoading} = value
  const [expectedTime,setExpectedTime] = useState(null)
  const [isExpectedTimeLoading, setExpectedTimeLoading] = useState(false)
  const {singleChosenBusId, setSingleChosenBusId} = value

  const [chosenLocation, setChosenLocation] = useState(null)
  const [nearbyRoutes, setNearbyRoutes] = useState(null)
  const [areNearbyRoutesLoading, setNearbyRoutesLoading] = useState(false)
  const [expectedTimes, setExpectedTimes] = useState(null)
  const [areExpectedTimesLoading, setExpectedTimesLoading] = useState(null)

  const [previewedIds, setPreviewedIds] = useState([])

  const {chosenRoute, setChosenRoute} = value
  const {chosenRouteIntervalId, setChosenRouteIntervalId} = value
  const {isChosenRouteLoading, setChosenRouteLoading} = value

  const [chosenBusStop, setChosenBusStop] = useState(null)
  const chosenBusStopRef = useRef(chosenBusStop)
  useEffect(() => {chosenBusStopRef.current=chosenBusStop},[chosenBusStop])

  //these refs are updated with the state so that functions have access to current value of state throught their .current
  //for functions passed that trigger at some event, the values of the states used inside it arent gonna be the ones at the triggerig of the function
  const singleBusRef = useRef(singleChosenBusId)
  const chosenBussesRef = useRef(chosenBusIds)
  const nearbyRoutesRef = useRef(nearbyRoutes)
  const chosenRouteRef = useRef(chosenRoute)
  const isUsingDirectionsRef = useRef(isUsingDirections)
  const chosenLocationRef = useRef(chosenLocation)
  useEffect(() => {chosenLocationRef.current=chosenLocation},[chosenLocation])
  const directionsResultsRef = useRef(directionsResults)
  useEffect(() => {directionsResultsRef.current=directionsResults},[directionsResults])
  const areDirectionsResultsLoadingRef = useRef(areDirectionsResultsLoading)
  useEffect(() => {areDirectionsResultsLoadingRef.current=areDirectionsResultsLoading},[areDirectionsResultsLoading])

  //this useEffect listens to isOnMapPage and toggles visibility of layers
  useEffect(() => {
    if(isMapLoaded){
      if(isOnMapPage){
        if(map.getLayer('bus-stop-route-layer')) map.setLayoutProperty('bus-stop-route-layer','visibility','visible')
        if(map.getLayer('user-live-location-layer')) map.setLayoutProperty('user-live-location-layer','visibility','visible')
        if(map.getLayer('busses-live-location-layer')) map.setLayoutProperty('busses-live-location-layer','visibility','visible')
        if(map.getLayer('pickup-point-layer')) map.setLayoutProperty('pickup-point-layer','visibility','visible')
        if(map.getLayer('pickup-point2-layer')) map.setLayoutProperty('pickup-point2-layer','visibility','visible')
        if(map.getLayer("remaining-route-top-layer")) map.setLayoutProperty("remaining-route-top-layer",'visibility','visible')
        if(map.getLayer("remaining-route-bottom-layer")) map.setLayoutProperty("remaining-route-bottom-layer",'visibility','visible')
        if(map.getLayer("chosen-route-bottom-layer")) map.setLayoutProperty("chosen-route-bottom-layer",'visibility','visible')
        if(map.getLayer("chosen-route-top-layer")) map.setLayoutProperty("chosen-route-top-layer",'visibility','visible')
        if(nearbyRoutesRef.current) nearbyRoutesRef.current.forEach((route) => {
          const id = `route-${route.route_id}-layer`
          if(map.getLayer(id)) map.setLayoutProperty(id,'visibility','visible')
        })
        if(directionsResultsRef.current) directionsResultsRef.current.forEach((route) => {
          const id = `route-${route.route_id}-layer`
          if(map.getLayer(id)) map.setLayoutProperty(id,'visibility','visible')
        })
        if(document.getElementById('marker')) document.getElementById('marker').style.visibility='visible'
        if(document.getElementById('start-marker')) document.getElementById('start-marker').style.visibility='visible'
        if(document.getElementById('destination-marker')) document.getElementById('destination-marker').style.visibility='visible'
      }
      else{
        if(map.getLayer('bus-stop-route-layer')) map.setLayoutProperty('bus-stop-route-layer','visibility','none')
        if(map.getLayer('user-live-location-layer')) map.setLayoutProperty('user-live-location-layer','visibility','none')
        if(map.getLayer('busses-live-location-layer')) map.setLayoutProperty('busses-live-location-layer','visibility','none')
        if(map.getLayer('pickup-point-layer')) map.setLayoutProperty('pickup-point-layer','visibility','none')
        if(map.getLayer('pickup-point2-layer')) map.setLayoutProperty('pickup-point2-layer','visibility','none')
        if(map.getLayer("remaining-route-top-layer")) map.setLayoutProperty("remaining-route-top-layer",'visibility','none')
        if(map.getLayer("remaining-route-bottom-layer")) map.setLayoutProperty("remaining-route-bottom-layer",'visibility','none')
        if(map.getLayer("chosen-route-bottom-layer")) map.setLayoutProperty("chosen-route-bottom-layer",'visibility','none')
        if(map.getLayer("chosen-route-top-layer")) map.setLayoutProperty("chosen-route-top-layer",'visibility','none')
        if(nearbyRoutesRef.current) nearbyRoutesRef.current.forEach((route) => {
          const id = `route-${route.route_id}-layer`
          if(map.getLayer(id)) map.setLayoutProperty(id,'visibility','none')
        })
        if(directionsResultsRef.current) directionsResultsRef.current.forEach((route) => {
          const id = `route-${route.route_id}-layer`
          if(map.getLayer(id)) map.setLayoutProperty(id,'visibility','none')
        })
        if(document.getElementById('marker')) document.getElementById('marker').style.visibility='hidden'
        if(document.getElementById('start-marker')) document.getElementById('start-marker').style.visibility='hidden'
        if(document.getElementById('destination-marker')) document.getElementById('destination-marker').style.visibility='hidden'
      }
    }
  },[isOnMapPage])

  const removeMarker = () => {if(document.getElementById('marker'))document.getElementById('marker').remove()}  
  const removeStartMarker = () => {if(document.getElementById('start-marker'))document.getElementById('start-marker').remove()}
  const removeDestinationMarker = () => {if(document.getElementById('destination-marker'))document.getElementById('destination-marker').remove()}

  //makes marker disappear when clicking on it
  marker._element.addEventListener('click', (e) => {
    if(!isOnMapPageRef.current) return;
    if( singleBusRef.current || nearbyRoutesRef.current || chosenBussesRef.current || chosenBusStopRef.current ){return;}
    e.stopPropagation()
    setChosenLocation(null)
    removeMarker()
  })
  startMarker._element.addEventListener('click',(e) => {
    if(!isOnMapPageRef.current) return;
    if(areDirectionsResultsLoadingRef.current || directionsResultsRef.current!=null) return;
    e.stopPropagation()
    setStartingPoint(null)
    removeStartMarker()
  })
  destinationMarker._element.addEventListener('click',(e) => {
    if(!isOnMapPageRef.current) return;
    if(areDirectionsResultsLoadingRef.current || directionsResultsRef.current!=null) return;
    e.stopPropagation()
    setDestination(null)
    removeDestinationMarker()
  })

  //doing setChosenBusIds(null) leads to removing all lines that were set as visible
  //NOTE: before fetching data, check if was loading or not

  //this functions fetches bus stops data and adds layers (has been changed)
  const setBusStops = async () => {
    if(map.getSource('bus-stops')) return;
    await axios.get('/api/station',{
      headers:{
        'Content-Type': 'application/json'
      }
    })
    .then((res) => {
        const data=res.data.content
        //adds source for bus stops
        map.addSource('bus-stops',{
          type: 'geojson',
          data: data
        })
        //gives it a layer
        map.addLayer({
          id: 'bus-stops-layer',
          type: 'symbol',
          source: 'bus-stops',
          minzoom: 10,
          layout: {
            'icon-image': 'bus'
          }
        })
        //listens to clicks on a bus stop
        map.on("click", "bus-stops-layer", (e) => {
          if(!isOnMapPageRef.current) return;
          //clear the previous timeout if it exists
          if(clickTimeout){
            clearTimeout(clickTimeout)
          }

          const clickedBusStop = e.features[0]
          //set a new timeout
          clickTimeout = setTimeout(() => {
            //if we were searching for routes or on vehicle info section or on busstop section
            if(singleBusRef.current || nearbyRoutesRef.current || chosenRouteRef.current){
              setSingleChosenBusId(null)
              setChosenBusIds(null)
              setChosenRoute(null)
            }
            //we are on directions page so we're choosing start or destination
            else if(isUsingDirectionsRef.current){
              if(!startingPointRef.current){
                setStartingPoint({
                  name: clickedBusStop.properties.stop_name,
                  coordinates: clickedBusStop.geometry.coordinates
                })
              }
              else if(!destinationRef.current){
                setDestination({
                  name: clickedBusStop.properties.stop_name,
                  coordinates: clickedBusStop.geometry.coordinates
                })
              }
              else{
                //both are chosen
                if(directionsResultsRef.current || areDirectionsResultsLoading){
                  //we searched for routes, lets go back to picking start and end (to be changed)(because i want to cancel fetching of data)
                  setChosenBusIds(null)
                  setDirectionsResultsLoading(false)
                }
                else{
                  //didnt even search for routes so it takes you back to search
                  setUsingDirections(false)
                }
              }
            }
            else{
              //these happen if we weren't on a specific page
              map.flyTo({center: clickedBusStop.geometry.coordinates})
              if(chosenBusStop==clickedBusStop.properties){
                //if this the same bus stop that was already selected
                return
              }
              else if(chosenBusStopRef.current!=null){
                //we changed bus stops
                map.removeLayer('bus-stop-route-layer')
                map.removeSource('bus-stop-route')
              }
              setChosenBusStop(clickedBusStop.properties)

              //adds source for route related to this bus stop
              map.addSource("bus-stop-route",{
                type:'geojson',
                //objects as values of a property are JSON.stringified automatically
                data: JSON.parse(clickedBusStop.properties.line)
              })
              //gives it a layer
              map.addLayer({
                id: 'bus-stop-route-layer',
                type: "line",
                source: 'bus-stop-route',
                layout: {
                    "line-join": "round",
                    "line-cap": "round"
                }, 
                paint: {
                    "line-color": "#5474d4", // same color as bus stop
                    "line-width": 4 // thin line
                }
              },'bus-stops-layer')
            }
          },350)
        })
      }
    )
    .catch()
  }

  //this useEffect waits for map to load and sets default event listeners
  useEffect(() => {
    if(isMapLoaded){

      //starts showing busses
      setShowingBusses(true)

      //listens to click and adds marker
      map.on("click", (e) => {
        if(!isOnMapPageRef.current) return;
        //these lines detect a single click on the map
        //array of all the features clicked that are part of 'user-live-location-layer', 'busses-live-location-layer', and 'route-bottom-layer''s
        const ullLayerFeatures = map.getLayer('user-live-location-layer') ? map.queryRenderedFeatures(e.point, { layers: ['user-live-location-layer'] }) : [];
        const bllLayerFeatures = map.getLayer('busses-live-location-layer') ? map.queryRenderedFeatures(e.point, { layers: ['busses-live-location-layer']}) : [];
        const rrLayerFeatures = map.getLayer('remaining-route-bottom-layer') ? map.queryRenderedFeatures(e.point, { layers: ['remaining-route-bottom-layer']}) : [];
        const crLayerFeatures = map.getLayer('chosen-route-bottom-layer') ? map.queryRenderedFeatures(e.point, { layers: ['chosen-route-bottom-layer']}) : [];
        const labelLayerFeatures = map.queryRenderedFeatures(e.point,{layers: ["bus-stops-layer","poi-label","airport-label","transit-label","water-point-label","state-label","settlement-major-label","settlement-minor-label","settlement-subdivision-label"]})
        // checks if the click WASN'T on any of them
        if(!ullLayerFeatures.length && !bllLayerFeatures.length && !rrLayerFeatures.length && !crLayerFeatures.length && !labelLayerFeatures.length){

          // clear previous timeout if it exists
          if(clickTimeout){
              clearTimeout(clickTimeout)
          }
          //set a new timeout
          clickTimeout = setTimeout(() => {
            //if we were searching for routes or on vehicle info section or on busstop section
            if(singleBusRef.current || nearbyRoutesRef.current || chosenRouteRef.current || chosenBusStopRef.current){
              setSingleChosenBusId(null)
              setChosenBusIds(null)
              setChosenRoute(null)
              setChosenBusStop(null)
            }
            //we are on directions page so we're choosing start or destination
            else if(isUsingDirectionsRef.current){
              if(!startingPointRef.current){
                startMarker.remove()
                startMarker.setLngLat(e.lngLat).addTo(map)
                setStartingPoint({
                  name: `${e.lngLat.lat.toFixed(6)}, ${e.lngLat.lng.toFixed(6)}`,
                  coordinates: [e.lngLat.lng, e.lngLat.lat],
                  isMarkedLocation: true
                })
              }
              else if(!destinationRef.current){
                destinationMarker.remove()
                destinationMarker.setLngLat(e.lngLat).addTo(map)
                setDestination({
                  name: `${e.lngLat.lat.toFixed(6)}, ${e.lngLat.lng.toFixed(6)}`,
                  coordinates: [e.lngLat.lng, e.lngLat.lat],
                  isMarkedLocation: true
                })
              }
              else{
                //both are chosen
                if(directionsResultsRef.current || areDirectionsResultsLoading){
                  //we searched for routes, lets go back to picking start and end (to be changed)(because i want to cancel fetching of data)
                  setChosenBusIds(null)
                  setDirectionsResultsLoading(false)
                }
                else{
                  //didnt even search for routes so it takes you back to search
                  setUsingDirections(false)
                }
              }
            }
            else{
              //we weren't on a specific bus or searching for routes

              //remove old marker
              marker.remove()
              //add new marker
              marker.setLngLat(e.lngLat).addTo(map)
              //fly the user to the marker
              map.flyTo({center: e.lngLat, zoom:Math.max(13,map.getZoom())})
              //set this as chosen location
              setChosenLocation({
                name: 'Marked Location',
                type: 'marked-location',
                coordinates: [e.lngLat.lng,e.lngLat.lat]
              })
            }
          },350)
        }
      })
      //makes sure it's not a double click
      map.on("zoom", () => {
          //clear the timeout
          if(clickTimeout){
              clearTimeout(clickTimeout)
          }
      })

      //detects a click on a label
      map.on("click", ["poi-label","airport-label","transit-label","water-point-label","state-label","settlement-major-label","settlement-minor-label","settlement-subdivision-label"], (e) => {
        if(!isOnMapPageRef.current) return;
        //clear the timeout
        if(clickTimeout){
          clearTimeout(clickTimeout)
        }
        const poi = e.features[0];
        //set a new timeout
        clickTimeout = setTimeout(() => {
          //if we were searching for routes or on vehicle info section or routes info section or bus stop section
          if(singleBusRef.current || chosenBussesRef.current || chosenRouteRef.current || chosenBusStopRef.current){
            setSingleChosenBusId(null)
            setChosenBusIds(null)
            setChosenRoute(null)
            setChosenBusStop(null)
          }
          else if(isUsingDirectionsRef.current){
            //we are on directions page
            if(!startingPointRef.current){
              setStartingPoint({
                name: poi.properties.name ? poi.properties.name :`${poi.geometry.coordinates[1].toFixed(6)}, ${poi.geometry.coordinates[0].toFixed(6)} `,
                coordinates: poi.geometry.coordinates
              })
            }
            else if(!destinationRef.current){
              setDestination({
                name: poi.properties.name ? poi.properties.name :`${poi.geometry.coordinates[1].toFixed(6)}, ${poi.geometry.coordinates[0].toFixed(6)} `,
                coordinates: poi.geometry.coordinates
              })
            }
            else{
              //both are chosen
              if(directionsResultsRef.current || areDirectionsResultsLoading){
                //we searched for routes, lets go back to picking start and end (to be changed)(because i want to cancel fetching of data)
                setChosenBusIds(null)
                setDirectionsResultsLoading(false)
              }
              else{
                //didnt even search for routes so it takes you back to search
                setUsingDirections(false)
              }
            }
          }
          else{
            //we weren't on a specific bus or searching for routes
            //remove marker if it was there
            marker.remove();
            setChosenLocation(null)
            //set this poi as chosen location
            setChosenLocation({
              name: poi.properties.name ? poi.properties.name :`${poi.geometry.coordinates[1].toFixed(6)}, ${poi.geometry.coordinates[0].toFixed(6)} `,
              type: 'poi',
              coordinates: poi.geometry.coordinates
            })
          }
        },350)
      })

      //fetches bus stops from API
      setBusStops()
    }
  
  },[isMapLoaded])

  //this useEffect listens to isUsingDirections
  useEffect(() => {
    isUsingDirectionsRef.current=isUsingDirections
    if(isUsingDirections){
      removeMarker()
      setChosenLocation(null)
    }
    else{
      removeStartMarker()
      removeDestinationMarker()
      setStartingPoint(null)
      setDestination(null)
    }
  },[isUsingDirections])
  useEffect(() => {
    startingPointRef.current=startingPoint
    if(!startingPoint){
      removeStartMarker()
    }
  },[startingPoint])
  useEffect(() => {
    destinationRef.current=destination
    if(!destination){
      removeDestinationMarker()
    }
  },[destination])

  //handles click of locate button in bottom left corner
  const handleLocateClick = () => {
    if(isMapLoaded){
      setSharingLocation(!isSharingLocation)
    }
  }

  //this useEffect listens to value of isSharingLocation
  useEffect( () => {
    if (isSharingLocation){
      //set inverval for fetching every 2 seconds
      const id = setInterval(() => {
        if (navigator.geolocation) {
          //geolocation is supported
          navigator.geolocation.getCurrentPosition(
            (position) => {
              //we successfully fetch position
              const { latitude, longitude } = position.coords;
              //updates live location state
              setLiveLocation([longitude,latitude])

              //if we never added a source for user live location, add it
              if(!map.getSource('user-live-location')){
                //removes marker if it was there
                removeMarker()
                setChosenLocation(null)
                //adds data source for user's live location
                map.addSource('user-live-location',{
                  type: 'geojson',
                  data: {
                    type: 'FeatureCollection',
                    features: [
                      {
                        type: 'Feature',
                        geometry: {
                          type: 'Point',
                          coordinates: [longitude, latitude]
                        }
                      }
                    ]
                  }
                })
                //gives it a layer
                map.addLayer({
                  id: 'user-live-location-layer',
                  type: 'symbol',
                  source: 'user-live-location',
                  layout: {
                    'icon-image': 'pulsing-blue-dot'
                  }
                })
                
                //action triggered when pressing on the pulsing blue dot
                map.on('click','user-live-location-layer',() => {
                  if(!isOnMapPageRef.current) return;
                  
                  //clear old timeout
                  if(clickTimeout){
                    clearTimeout(clickTimeout)
                  }
                  //set a new timeout
                  clickTimeout = setTimeout(() => {
                    //if we were searching for routes or on vehicle info section or routes info section or bus stop section
                    if(singleBusRef.current || chosenBussesRef.current || chosenRouteRef.current || chosenBusStopRef.current){
                      setSingleChosenBusId(null)
                      setChosenBusIds(null)
                      setChosenRoute(null)
                      setChosenBusStop(null)
                    }
                    else if(isUsingDirectionsRef.current){
                      //we are on directions page
                      if(!startingPointRef.current){
                        setStartingPoint({
                          name: 'Current Location',
                          coordinates: liveLocationRef.current
                        })
                      }
                      else if(!destinationRef.current){
                        setDestination({
                          name: 'Current Location',
                          coordinates: liveLocationRef.current
                        })
                      }
                      else{
                        //both are chosen
                        if(directionsResultsRef.current || areDirectionsResultsLoading){
                          //we searched for routes, lets go back to picking start and end (to be changed)(because i want to cancel fetching of data)
                          setChosenBusIds(null)
                          setDirectionsResultsLoading(false)
                        }
                        else{
                          //didnt even search for routes so it takes you back to search
                          setUsingDirections(false)
                        }
                      }
                    }
                    else{
                      //we weren't on a specific bus or searching for routes
                      //remove marker if it was there
                      removeMarker()
                      //choose location and pan to it
                      setChosenLocation({
                        name: 'Current Location',
                        type: 'user-live-location',
                        coordinates: liveLocationRef.current
                      })
                      map.flyTo({center: liveLocationRef.current, zoom: Math.max(16,map.getZoom())})
                    }
                  },350)
                })
                if(isUsingDirectionsRef.current){
                  //we are on directions page
                  if(!startingPointRef.current){
                    setStartingPoint({
                      name: 'Current Location',
                      coordinates: [longitude, latitude]
                    })
                  }
                  else if(!destinationRef.current){
                    setDestination({
                      name: 'Current Location',
                      coordinates: [longitude, latitude]
                    })
                  }
                }
                else if(!isUsingDirectionsRef.current && !nearbyRoutesRef.current && !directionsResultsRef.current){
                  // sets chosen location to current location
                  setChosenLocation({
                    name: 'Current Location',
                    type: 'user-live-location',
                    coordinates: [longitude, latitude]
                  })
                }
                if(isOnMapPageRef.current){
                  //flies to location if we just clicked the button
                  map.flyTo({center: [longitude,latitude], zoom: Math.max(16,map.getZoom())})
                }
                else{
                  //hide the pulsing dot until we go o /map
                  map.setLayoutProperty('user-live-location-layer','visibility','none')
                }
              }
              else{
                //gets source and updates its data
                const locationSource = map.getSource('user-live-location')
                locationSource.setData({
                  type: 'FeatureCollection',
                  features: [
                    {
                      type: 'Feature',
                      geometry: {
                        type: 'Point',
                        coordinates: [longitude, latitude]
                      }
                    }
                  ]
                })
                // if live location was currently chosen, update chosen location info
                if(chosenLocation!=null && chosenLocation.type=='user-live-location'){
                  setChosenLocation({
                    name: 'My Current Location',
                    type: 'user-live-location',
                    coordinates: [longitude, latitude]
                  })
                }
              }
            },
            (error) => {
                // display an error if we cant get the users position
                console.error('Error getting user location:', error);
                setTimeout(() => {
                  setSharingLocation(false); // Only set to false after a delay
                }, 5000); // Retry after 5 seconds
            }
        );
        }
        else {
            //geolocation is not supported
            // display an error if not supported
            console.error('Geolocation is not supported by this browser.');
            //stop sharing location
            setSharingLocation(false)
        }
      },2000)//updates location every 2 seconds
      setLocationIntervalId(id);
    }
    else{
      //not sharing location now
      //stop fetching live location
      clearInterval(locationIntervalId)

      //removing the dot if it was there
      if(isMapLoaded){
        if(map.getLayer('user-live-location-layer')) map.removeLayer('user-live-location-layer')
        if(map.getSource('user-live-location')) map.removeSource('user-live-location')
      }
      //if chosen location was current location, unchoose it
      if(chosenLocation && chosenLocation.type=='user-live-location'){
        setChosenLocation(null)
      }
    }
  },[isSharingLocation])

  //handles click of show busses button
  const handleShowBussesClick = () => {
    if(value.isMapLoaded){
      setShowingBusses(!isShowingBusses)
    }
  }

  //fetches bus data from api (has been changed)
  const fetchBussesData = async () => {
    //new version
    await axios.get('/api/all_vehicles_location',{
      headers: {
        'Content-Type':'application/json'
      }
    })
    .then((res) => {
        if(res.status==200){
          setBusData(res.data.content.features)
        }
      }
    )
    .catch((e) => {
      setShowingBusses(false)
    })
  }

  //fetches ETA from bus to pickup point in minutes (has been changed)
  const fetchETA = async (id, pickup_point) => {
    const [lng, lat] = pickup_point.geometry.coordinates
    await axios.get(`/api/vehicle_eta/${id}?pick_up_long=${lng}&pick_up_lat=${lat}`,{
      headers: {
        "Content-Type": "application/json"
      }
    })
    .then((res) => {
        if(res.status==200){
          if(!res.data.content.passed){
            setExpectedTime(res.data.content.expected_time)
          }
          else{
            setExpectedTime(0)
          }
          setExpectedTimeLoading(false)
        }
      }
    )
    .catch((e) => {
      if(e.response.status==422 || e.response.status== 404){
        setExpectedTimeLoading(false)
      }
    })
  }

  //fetches ETA from every bus on route to pickup point in minutes (to be changed)
  const fetchETAs = async (route_id, pickup_point) => {
    const [lng, lat] = pickup_point.geometry.coordinates
    await axios.get(`/api/route_vehicles_eta/${route_id}?pick_up_long=${lng}&pick_up_lat=${lat}`,{
      headers: {
        "Content-Type": "application/json"
      }
    })
    .then((res) => {
        if(res.status==200){
          setExpectedTimes(res.data.vehicles)
          setExpectedTimesLoading(false)
        }
      }
    )
    .catch((e) => {
      if(e.response.status==404 || e.response.status==422){
        setExpectedTimesLoading(false)
      }
    })
  }

  //this useEffect listens to value of busData/highlighted busses and updates
  useEffect(() => {
    //update refs
    chosenBussesRef.current=chosenBusIds
    singleBusRef.current=singleChosenBusId

    if(!chosenBusIds){
      //if we were on nearby routes page and now we're out of it
      setPreviewedIds([])

      //remove any route we were showing
      if(nearbyRoutes){
        nearbyRoutes.forEach((e) => {
          if(map.getLayer(`route-${e.route_id}-layer`)) map.removeLayer(`route-${e.route_id}-layer`)
          if(map.getSource(`route-${e.route_id}`)) map.removeSource(`route-${e.route_id}`)
        })
      }
      if(directionsResults){
        directionsResults.forEach((e) => {
          if(map.getLayer(`route-${e.route_id}-layer`)) map.removeLayer(`route-${e.route_id}-layer`)
          if(map.getSource(`route-${e.route_id}`)) map.removeSource(`route-${e.route_id}`)
        })
      }
      //delete all the data
      setDirectionsResults(null)
      setNearbyRoutes(null)
    }
    if(!singleChosenBusId){

      //if we were on a specific route page before closing specific bus page, we wanna show its route
      if(chosenRoute && isOnMapPage){
        if(map.getLayer('chosen-route-top-layer'))map.setLayoutProperty('chosen-route-top-layer','visibility','visible')
        if(map.getLayer('chosen-route-bottom-layer'))map.setLayoutProperty('chosen-route-bottom-layer','visibility','visible')
        if(map.getLayer('pickup-point2-layer'))map.setLayoutProperty('pickup-point2-layer','visibility','visible')
      }
      //nothing is chosen now
      setChosenBusData(null)
      setLookingAtBus(false)
      //stop fetching live detailed info about chosen bus
      clearInterval(chosenBusIntervalId)
      //must remove layer before source
      if(isMapLoaded){
        if(map.getLayer('remaining-route-top-layer')) map.removeLayer('remaining-route-top-layer')
        if(map.getLayer('remaining-route-bottom-layer')) map.removeLayer('remaining-route-bottom-layer')
        if(map.getSource('remaining-route')) map.removeSource('remaining-route')
        if(map.getLayer('pickup-point-layer')) map.removeLayer('pickup-point-layer')
        if(map.getSource('pickup-point')) map.removeSource('pickup-point')
      }
    }
    else{
      // we are now on a specific bus page

      //unselect bus stop if it was selected
      setChosenBusStop(null)

      //if we were on the nearby routes page, we wanna hide every line we were showing
      if(nearbyRoutes){
        nearbyRoutes.forEach((route) => {
          const layerId=`route-${route.route_id}-layer`
          if(map.getLayer(layerId)) map.setLayoutProperty(layerId,'visibility','none')
        })
      }
      //if we were on directions routes page, we wanna hide every line we were showing
      if(directionsResults){
        directionsResults.forEach((route) => {
          const layerId=`route-${route.route_id}-layer`
          if(map.getLayer(layerId)) map.setLayoutProperty(layerId,'visibility','none')
        })
      }

      //if we were on a specific route page, we wanna hide its route
      if(chosenRoute){
        map.setLayoutProperty('chosen-route-top-layer','visibility','none')
        map.setLayoutProperty('chosen-route-bottom-layer','visibility','none')
        map.setLayoutProperty('pickup-point2-layer','visibility','none')
      }
    }
    if(isShowingBusses && busData){
      // want to update what's shown on the map
      // busData is gonna be the features array
      var shownData = busData
      //checks if there is some greying out (specific bus section or routes section)
      if(chosenBusIds || singleChosenBusId || chosenRoute){
        //taking ids from chosenRoute.vehicles
        const chosenRouteIds = chosenRoute ? chosenRoute.vehicles.map((e) => e.id) : []

        //want to highlight only the chosen busses

        shownData = busData.map((bus) => {
          //single bus selection doesnt need chosenbusses selection
          //chosenroute filtering only happens if we're not looking at singlebus
          //chosenbusses filtering only happens if we're not looking at singlebus or chosenroute
          if((chosenBusIds && chosenBusIds.includes(bus.properties.id) && !singleChosenBusId && !chosenRoute) || (chosenRoute && chosenRouteIds.includes(bus.properties.id) && !singleChosenBusId) || (singleChosenBusId && singleChosenBusId==bus.properties.id)){
            //it's supposed to be highlighted (remove m if it's there)
            if(bus.properties.status.charAt(bus.properties.status.length-1)=='m'){
              return {...bus, properties:{
                id: bus.properties.id,
                status: bus.properties.status.substring(0,bus.properties.status.length-1)
              }}
            }
            return bus
          }
          //it's supposed to be greyed out (add m if it's not there)
          if(bus.properties.status.charAt(bus.properties.status.length-1)!='m'){
            return {...bus, properties:{
              id: bus.properties.id,
              status: bus.properties.status+"m"
            }}
          }
          return bus
        })
        if(lookingAtBus){
          if(chosenBusIntervalId) clearInterval(chosenBusIntervalId)
          const id = setInterval(() => {
            fetchChosenBusData(singleChosenBusId)
          },2000)
          setChosenBusIntervalId(id)
        }
      }
      else{
        //there is no highlighting
        //if were fetching specific info abt vehicle, stop
        if(chosenBusIntervalId) clearInterval(chosenBusIntervalId)
      }
      // adds bus location source if wasn't already there
      if(!map.getSource('busses-live-location')){
        map.addSource('busses-live-location',{
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features : shownData
          }
        })
        // this adds the layer for the busses, logic is, when we search for routes
        // we append some letter to the end of the status of each feature, and when we show 
        // a route, to remove that letter from all the features that are on that road, and therfore highlighting them

        map.addLayer({
          id: 'busses-live-location-layer',
          type: 'symbol',
          source: 'busses-live-location',
          minzoom: 11.5,
          layout: {
            'icon-image': ['match',['get','status'],
              'active', 'static-green-dot',
              'waiting', 'static-yellow-dot',
              'unavailable', 'static-red-dot',
              'static-grey-dot'
            ]
          }
        })

        //if we're not on /map, hide them for now
        if(!isOnMapPageRef.current){
          map.setLayoutProperty('busses-live-location-layer','visibility','none')
        }
        //listens to a click on a bus
        map.on('click', 'busses-live-location-layer', (e) => {
          if(!isOnMapPageRef.current) return;

          //if we pressed on the same bus we were on
          if(e.features[0].properties.id==singleBusRef.current) return;
      
          if(chosenLocationRef.current && chosenLocationRef.current.type=='marked-location') removeMarker()
          setChosenLocation(null)
          setChosenBusStop(null)

          setLookingAtBus(true)

          //reset everything related to pickup point(if we switched busses)
          setExpectedTime(null)
          setExpectedTimeLoading(false)
          if(map.getLayer('remaining-route-top-layer')) map.removeLayer('remaining-route-top-layer')
          if(map.getLayer('remaining-route-bottom-layer')) map.removeLayer('remaining-route-bottom-layer')
          if(map.getSource('remaining-route')) map.removeSource('remaining-route')
          if(map.getLayer('pickup-point-layer')) map.removeLayer('pickup-point-layer')
          if(map.getSource('pickup-point')) map.removeSource('pickup-point')

          const clickedBus = e.features[0] //this is the feature object that was clicked on
          map.flyTo({center: clickedBus.geometry.coordinates, zoom: Math.max(16, map.getZoom())})//flyTo without setting the zoom keeps original zoom
          setSingleChosenBusId(clickedBus.properties.id)
          setChosenBusDataLoading(true)
          fetchChosenBusData(clickedBus.properties.id)
        })
      }
      else{
        //there is already a source, just update it
        const source= map.getSource('busses-live-location')
        source.setData({
          type: 'FeatureCollection',
          features : shownData
        })
      }
    }
    else{
      //not showing busses, remove source and layers if they're present
      if(isMapLoaded){
        if(map.getLayer('busses-live-location-layer')) map.removeLayer('busses-live-location-layer')
        if(map.getSource('busses-live-location')) map.removeSource('busses-live-location')
      }
    }
  },[busData,chosenBusIds, singleChosenBusId, chosenRoute])

  //this function handles a click on remaining route
  const handleRemainingRouteClick = (e) => {
    if(!isOnMapPageRef.current) return;
    //anything a click would've normally triggered is stopped
    if(clickTimeout) clearTimeout(clickTimeout)
    //this will trigger as long no other click happens (dbl click maybe)
    clickTimeout = setTimeout(() => {
      //takes line and point, and returns closest point on that line
      const nearest= turf.nearestPointOnLine(chosenBusData.remaining_route,{type: "Point",coordinates: [e.lngLat.lng,e.lngLat.lat]})        
      //pickup point is added initially but with no point, so we set data
      map.getSource('pickup-point').setData({
        type: 'FeatureCollection',
        features: [nearest]
      })
      //want to get ETA
      setExpectedTimeLoading(true)
      setExpectedTime(null)
      fetchETA(singleBusRef.current,nearest)
    },200)
  }
  const addedListener1 = useRef(false)

  //this useEffect listens to value of isShowingBusses and starts/stops constant fetching
  useEffect(() => {
    if(isShowingBusses){
      ///start fetching location data of all busses every 2 seconds
      const id = setInterval(() => {
        fetchBussesData()
      },2000)
      setBussesInvervalId(id)
    }
    else{
      //delete data
      setBusData(null)
      //stop fetching
      clearInterval(bussesIntervalId)
    }
  },[isShowingBusses])

  //this useEffect listens to value of chosenBusData / changes to single chosen bus and updates remaining route
  useEffect(() => {
    if(!isMapLoaded) return; //self explanatory
    if(chosenBusData){
      const oldSource = map.getSource('remaining-route')
      if(oldSource){
        //there was data
        if(chosenBusData.status=='inactive' || chosenBusData.status=='unknown'){
          //bus is now inactive, remove everything
          if(map.getLayer('remaining-route-bottom-layer')) map.removeLayer('remaining-route-bottom-layer')
          if(map.getLayer('remaining-route-top-layer')) map.removeLayer('remaining-route-top-layer')
          if(map.getSource('remaining-route')) map.removeSource('remaining-route')
          if(map.getLayer('pickup-point-layer')) map.removeLayer('pickup-point-layer')
          if(map.getSource('pickup-point')) map.removeSource('pickup-point')
        }
        else{
          //update remaining route
          oldSource.setData({
            type: 'FeatureCollection',
            features: [chosenBusData.remaining_route]
          })
        }
      }
      else{
        //there is no source
        if(chosenBusData.status!='inactive' && chosenBusData.status!='unknown'){
          //bus isn't inactive or unknown so had remaining route, so add sources and layers

          //source for remaining route
          map.addSource('remaining-route',{
            type: "geojson",
            data:{
              type: 'FeatureCollection',
              features: [chosenBusData.remaining_route]
            }
          })
          //visible layer
          map.addLayer({
            id: "remaining-route-top-layer",
            type: "line",
            source: 'remaining-route',
            layout: {
               "line-join": "round",
                "line-cap": "round"
            }, 
            paint: {
                "line-color": "#4050DE", // blue color
                "line-width": 4 // thin line
            }
          },'bus-stops-layer')
          //invisible hitbox layer
          map.addLayer({
            id: "remaining-route-bottom-layer",
            type: "line",
            source: 'remaining-route',
            layout: {
               "line-join": "round",
                "line-cap": "round"
            }, 
            paint: {
                "line-color": "#4050DE",
                "line-width": 20,
                "line-opacity": 0.01 //barely visible
            }
          },'remaining-route-top-layer')//put this layer beneath the visible layer
          
          //source and layer for picking a pickup point
          map.addSource('pickup-point',{
            type: 'geojson',
            data:{
              type: 'FeatureCollection',
              features: []
            }
          })
          map.addLayer({
            id: 'pickup-point-layer',
            type: 'symbol',
            source: 'pickup-point',
            layout: {
              'icon-image': 'static-blue-dot'
            }
          },'bus-stops-layer')

          //listens to click on hitbox layer
          if(!addedListener1.current){
            map.on("click","remaining-route-bottom-layer",handleRemainingRouteClick)
            addedListener1.current=true
          }
          
        }
        else{
          //bus is actually inactive
          if(map.getLayer('pickup-point-layer')) map.removeLayer('pickup-point-layer')
          if(map.getSource('pickup-point')) map.removeSource('pickup-point')
          if(map.getLayer('remaining-route-bottom-layer')) map.removeLayer('remaining-route-bottom-layer')
          if(map.getLayer('remaining-route-top-layer')) map.removeLayer('remaining-route-top-layer')
          if(map.getSource('remaining-route')) map.removeSource('remaining-route')
        }
      }
    }
    else{
      //we're no longer on specific bus section
      //stop fetching live detailed info about chosen bus
      clearInterval(chosenBusIntervalId)
      //remove all layers and sources
      if(map.getLayer('pickup-point-layer')) map.removeLayer('pickup-point-layer')
      if(map.getSource('pickup-point')) map.removeSource('pickup-point')
      if(map.getLayer('remaining-route-bottom-layer')) map.removeLayer('remaining-route-bottom-layer')
      if(map.getLayer('remaining-route-top-layer')) map.removeLayer('remaining-route-top-layer')
      if(map.getSource('remaining-route')) map.removeSource('remaining-route')
    }
  },[chosenBusData, singleChosenBusId])

  //fetches routes nearby certain location (to be changed)
  const fetchNearbyRoutes = async (chosenLocation) => {

    const [longitude, latitude] = chosenLocation.coordinates
    await axios.get(`/api/nearby_routes?long=${longitude}&lat=${latitude}&radius=500`,{
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then((res) => {
        if(res.status==200){
          setNearbyRoutes(res.data.routes)
          setNearbyRoutesLoading(false)
        }
      }
    )
    .catch((e) => {
      setNearbyRoutes([])
      setNearbyRoutesLoading(false)
    })
  }

  //fetches routes or chains of routes going from start to destination (has been changed)
  const fetchDirectionsRoutes = async (start,destination) => {
    const [longitude1, latitude1] = start.coordinates
    const [longitude2, latitude2] = destination.coordinates
    await axios.get(`/api/nearby_routes?long=${longitude1}&lat=${latitude1}&radius=500&long2=${longitude2}&lat2=${latitude2}&radius2=500`,{
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then((res) => {
        if(res.status==200){
          setDirectionsResults(res.data.routes)
          setDirectionsResultsLoading(false)
        }
      }
    )
    .catch((e) => {
      setDirectionsResults([])
      setDirectionsResultsLoading(false)
    })
  }

  //handles click of nearby routes button in the bottom middle
  const handleNearbyRoutesClick = () => {
    //start looking for routes
    setNearbyRoutesLoading(true)
    fetchNearbyRoutes(chosenLocation)
  }

  //handle click of search routes in directions section
  const handleSearchRoutesClick = (start,destination) => {
    //start looking for routes or chains of routes
    setDirectionsResultsLoading(true)
    fetchDirectionsRoutes(start,destination)
  }

  //handles click of view full route button in BusDataCard or BusStopCard
  const handleViewFullRouteClick = (route_id) => {
    setSingleChosenBusId(null)
    setChosenBusStop(null)
    if(!chosenRouteRef.current){
      setChosenRouteLoading(true)
      fetchRouteData(route_id)
      setChosenRouteIntervalId(setInterval(() => {
        fetchRouteData(route_id)
      },2000))
    }
    else{
      // we chose this bus from a route page

      if(route_id==chosenRouteRef.current.route_id){
        //this is the same as the old route, just go back to showing it
        
        // zoom out in a way that shows the whole route
        // wanna find extent of this route
        var [minLat,maxLat,minLng,maxLng] = [200,-200,200,-200]
        chosenRoute.line.features[0].geometry.coordinates.forEach((p) => {
          minLng=Math.min(minLng,p[0])
          maxLng=Math.max(maxLng,p[0])
          minLat=Math.min(minLat,p[1])
          maxLat=Math.max(maxLat,p[1])
        })
        //defining the bounding box for the route and going to it
        const point1 = [minLng, minLat]
        const point2 = [maxLng, maxLat]
        const bounds = [point1, point2]
        map.fitBounds(bounds,{padding: 100})
      }
      else{
        //we were on a route, we went to a bus on another route and viewed that bus' full route
        //remove the old route
        setChosenRoute(null)
        //wait 100 ms so the effects of setting chosen route to null take place
        setTimeout(() => {
          setChosenRouteLoading(true)
          fetchRouteData(route_id)
          setChosenRouteIntervalId(setInterval(() => {
            fetchRouteData(route_id)
          },2000))
        },100)
        
      }
    }
  }

  //listens to whether user is searching for routes
  useEffect(() => {
    //update the ref
    nearbyRoutesRef.current=nearbyRoutes
    if(areNearbyRoutesLoading || nearbyRoutes!=null || areDirectionsResultsLoading || directionsResults!=null){
      //make everything greyed out
      setChosenBusIds([])
    }
    else{
      setChosenBusIds(null)
    }
  },[areNearbyRoutesLoading, nearbyRoutes, areDirectionsResultsLoading, directionsResults])

  //this function handles a click on chosen route
  const handleChosenRouteClick = (e) => {
    if(!isOnMapPageRef.current) return;
    //anything a click would've normally triggered is stopped
    if(clickTimeout) clearTimeout(clickTimeout)
    //this will trigger as long no other click happens (dbl click maybe)
    clickTimeout = setTimeout(() => {
      //takes line and point, and returns closest point on that line
      const nearest= turf.nearestPointOnLine(chosenRouteRef.current.line,{type: "Point",coordinates: [e.lngLat.lng,e.lngLat.lat]})        
      //pickup point is added initially but with no point, so we set data
      map.getSource('pickup-point2').setData({
        type: 'FeatureCollection',
        features: [nearest]
      })
      //want to get ETAs
      setExpectedTimes(null)
      setExpectedTimesLoading(true)
      fetchETAs(chosenRouteRef.current.route_id,nearest)
    },150)
  }
  const addedListener2 = useRef(false)

  //listens to whether user has chosen a route
  useEffect(() => {
    chosenRouteRef.current=chosenRoute
    if(chosenRoute){
      //unselect bus stop if it was selected
      setChosenBusStop(null)

      //if we were on the nearby routes page and chose a route, we wanna hide every line we were showing
      if(nearbyRoutes){
        nearbyRoutes.forEach((route) => {
          const layerId=`route-${route.route_id}-layer`
          if(map.getLayer(layerId)) map.setLayoutProperty(layerId,'visibility','none')
        })
      }
      //if we were on directions routes page and chose a route, we wanna hide every line we were showing
      if(directionsResults){
        directionsResults.forEach((route) => {
          const layerId=`route-${route.route_id}-layer`
          if(map.getLayer(layerId)) map.setLayoutProperty(layerId,'visibility','none')
        })
      }

      //source and layer for picking a pickup point
      // this one is diff than the one for specific bus section
      if(!map.getSource('chosen-route')){
        map.addSource('pickup-point2',{
          type: 'geojson',
          data:{
            type: 'FeatureCollection',
            features: []
          }
        })
        map.addLayer({
          id: 'pickup-point2-layer',
          type: 'symbol',
          source: 'pickup-point2',
          layout: {
            'icon-image': 'static-blue-dot'
          }
        },'bus-stops-layer')

        //add Source
        map.addSource('chosen-route',{
          type: 'geojson',
          data: chosenRoute.line
        })
        //visible layer
        map.addLayer({
          id: "chosen-route-top-layer",
          type: "line",
          source: 'chosen-route',
          layout: {
            "line-join": "round",
              "line-cap": "round"
          }, 
          paint: {
              "line-color": "#4050DE", // blue color
              "line-width": 4 // thin line
          }
        },'pickup-point2-layer')
        //invisible hitbox layer
        if(map.getLayer('chosen-route-bottom-layer')) map.removeLayer('chosen-route-bottom-layer')//remove old layer
        map.addLayer({
          id: "chosen-route-bottom-layer",
          type: "line",
          source: 'chosen-route',
          layout: {
            "line-join": "round",
              "line-cap": "round"
          }, 
          paint: {
              "line-color": "#4050DE",
              "line-width": 20,
              "line-opacity": 0.01 //barely visible
          }
        },'chosen-route-top-layer')//put this layer beneath the visible layer

        if(!addedListener2.current){
          //listens to click on hitbox layer
          map.on("click","chosen-route-bottom-layer",handleChosenRouteClick)
        }  

        // zoom out in a way that shows the whole route
        // wanna find extent of this route
        var [minLat,maxLat,minLng,maxLng] = [200,-200,200,-200]
        chosenRoute.line.features[0].geometry.coordinates.forEach((p) => {
          minLng=Math.min(minLng,p[0])
          maxLng=Math.max(maxLng,p[0])
          minLat=Math.min(minLat,p[1])
          maxLat=Math.max(maxLat,p[1])
        })
        //defining the bounding box for the route and going to it
        const point1 = [minLng, minLat]
        const point2 = [maxLng, maxLat]
        const bounds = [point1, point2]
        map.fitBounds(bounds,{padding: 100})
      }
    }
    else{
      //reset expected times data
      setExpectedTimesLoading(false)
      setExpectedTimes(null)
      //stop fetching route data
      clearInterval(chosenRouteIntervalId)
      if(isMapLoaded){
        if(map.getLayer('pickup-point2-layer')) map.removeLayer('pickup-point2-layer')
        if(map.getSource('pickup-point2')) map.removeSource('pickup-point2')
        if(map.getLayer('chosen-route-top-layer')) map.removeLayer('chosen-route-top-layer')
        if(map.getLayer('chosen-route-bottom-layer')) map.removeLayer('chosen-route-bottom-layer')
        if(map.getSource('chosen-route')) map.removeSource('chosen-route')
      }
    }
  },[chosenRoute])

  //listens to whether user has clicked off a bus stop and removes bus stop route
  useEffect(() => {
    if(isMapLoaded){
      if(!chosenBusStop){
        if(map.getLayer('bus-stop-route-layer')) map.removeLayer('bus-stop-route-layer')
        if(map.getSource('bus-stop-route')) map.removeSource('bus-stop-route')
      }
    }
  },[chosenBusStop])

  //listens to visited busses and adds them to history
  useEffect(() => {
    if(chosenBusData){
      const busHistoryItem = {
        license_plate: chosenBusData.vehicle.license_plate,
        id: chosenBusData.id
      }
      const oldHistory = JSON.parse(localStorage.getItem('busses-history'))
      const newHistory = JSON.stringify([busHistoryItem].concat(oldHistory.filter((item) => JSON.stringify(item)!=JSON.stringify(busHistoryItem))))
      localStorage.setItem('busses-history',newHistory)
    }
  },[chosenBusData])
  //listens to visited routes and adds them to history
  useEffect(() => {
    if(chosenRoute){
      const routeHistoryItem = {
        route_name: chosenRoute.route_name,
        route_id: chosenRoute.route_id
      }
      const oldHistory = JSON.parse(localStorage.getItem('routes-history'))
      const newHistory = JSON.stringify([routeHistoryItem].concat(oldHistory.filter((item) => JSON.stringify(item)!=JSON.stringify(routeHistoryItem))))
      localStorage.setItem('routes-history',newHistory)
    }
  },[chosenRoute])

  return (
    isOnMapPage &&
    
    (needsToLogin ?
    <NeedToLoginPrompt message={message} setNeedsToLogin={setNeedsToLogin}/>
    :
    needsToGiveNickname ?
    <GiveNicknamePrompt vehicle={chosenBusData} setNeedsToGiveNickname={setNeedsToGiveNickname}/>
    :
    <div className='absolute z-10 pointer-events-none w-full h-screen flex flex-col justify-between p-3 border-b-[64px] md:border-b-[56px]'>
      {!chosenBusStop ?
      <>
      {!lookingAtBus ?
      <>
      {(!chosenRoute && !isChosenRouteLoading) ? //we are not looking at a specific route or a specific bus or bus stop
      <>
      <div className='flex justify-center md:justify-normal'>
        {(areNearbyRoutesLoading || nearbyRoutes!=null) ? 
        <NearbyRoutesResults
        areNearbyRoutesLoading={areNearbyRoutesLoading}
        setNearbyRoutesLoading={setNearbyRoutesLoading}
        nearbyRoutes={nearbyRoutes}
        setChosenBusIds={setChosenBusIds}
        chosenBusIds={chosenBusIds}
        previewedIds={previewedIds}
        setPreviewedIds={setPreviewedIds}
        />
        :
        isUsingDirections ?
        (
        (directionsResults!=null || areDirectionsResultsLoading) ?
        <DirectionsResults
        directionsResults={directionsResults}
        areDirectionsResultsLoading={areDirectionsResultsLoading}
        startingPoint={startingPoint}
        destination={destination}
        setChosenBusIds={setChosenBusIds}
        setDirectionsResultsLoading={setDirectionsResultsLoading}
        previewedIds={previewedIds}
        setPreviewedIds={setPreviewedIds}
        />
        :
        <DirectionsSearch
        setUsingDirections={setUsingDirections}
        setSharingLocation={setSharingLocation}
        liveLocation={liveLocation}
        startingPoint={startingPoint}
        setStartingPoint={setStartingPoint}
        destination={destination}
        setDestination={setDestination}
        handleSearchRoutesClick={handleSearchRoutesClick}
        />
        )   
        :
        <LocationSearchBar
        setChosenLocation={setChosenLocation}
        setUsingDirections={setUsingDirections}
        />
        }
      </div>
      <div className='flex flex-col'>
        <div className='flex justify-between'>
          <ShowBussesButton
           isShowingBusses={isShowingBusses}
           handleShowBussesClick={handleShowBussesClick}
          />
          { (chosenLocation!=null && !areNearbyRoutesLoading && nearbyRoutes==null) &&
            <NearbyRoutesButton 
            chosenLocation={chosenLocation} 
            handleNearbyRoutesClick={handleNearbyRoutesClick}
            />
          }
          <LocateButton
          handleLocateClick={handleLocateClick}
          isSharingLocation={isSharingLocation}
          />
        </div>
      </div>
      </>
      :
      //we're looking at a specific route
      <>
      <div className="flex flex-col justify-center items-center">
        <div
        className='mb-3 pointer-events-auto w-full max-w-96 flex justify-center items-center h-14 lg:h-12 rounded-xl bg-white opacity-90 hover:opacity-100 shadow-md cursor-pointer transition duration-200'
        onClick={() => setChosenRoute(null)}
        >
            <h1 className='text-gray4 text-[18px] lg:text-[16px]'>Click here or on the map to close</h1>
        </div>
        {(isShowingBusses && busData) &&
        <ExpectedTimesCard
        expectedTimes={expectedTimes}
        areExpectedTimesLoading={areExpectedTimesLoading}
        />
        }
      </div>
      <div className='flex justify-center md:justify-normal'>
          <BussesOnRouteCard
          isShowingBusses={isShowingBusses}
          busData={busData}
          setChosenBusIntervalId={setChosenBusIntervalId}
          expectedTimes={expectedTimes}
          areExpectedTimesLoading={areExpectedTimesLoading}
          isChosenRouteLoading={isChosenRouteLoading}
          chosenRoute={chosenRoute}
          setMessage={setMessage}
          setNeedsToLogin={setNeedsToLogin}
          />
      </div>
      </>
      }
      </>
    :
    //we are looking at a specific bus
      <>
      <div className="flex flex-col justify-center items-center">
        <div
        className='mb-3 pointer-events-auto w-full max-w-96 flex justify-center items-center h-14 lg:h-12 rounded-xl bg-white opacity-90 hover:opacity-100 shadow-md cursor-pointer transition duration-200'
        onClick={() => setSingleChosenBusId(null)}
        >
            <h1 className='text-gray4 text-[18px] lg:text-[16px]'>Click here or on the map to close</h1>
        </div>
        <ExpectedTimeCard
        expectedTime={expectedTime}
        isExpectedTimeLoading={isExpectedTimeLoading}
        />
      </div>
      <div className='flex justify-center md:justify-normal'>
        <BusDataCard
        isChosenBusDataLoading={isChosenBusDataLoading}
        chosenBusData={chosenBusData}
        handleViewFullRouteClick={handleViewFullRouteClick}
        setMessage={setMessage}
        setNeedsToLogin={setNeedsToLogin}
        setNeedsToGiveNickname={setNeedsToGiveNickname}
        />
      </div>
      </>
    }
    </>
    :
    //we are looking at a bus stop
    <>
    <div className='flex justify-center'>
        <div
        className='mb-3 pointer-events-auto w-full max-w-96 flex justify-center items-center h-14 lg:h-12 rounded-xl bg-white opacity-90 hover:opacity-100 shadow-md cursor-pointer transition duration-200'
        onClick={() => setChosenBusStop(null)}
        >
            <h1 className='text-gray4 text-[18px] lg:text-[16px]'>Click here or on the map to close</h1>
        </div>
    </div>
    <div className='flex justify-center md:justify-normal'>
      <BusStopDataCard
      handleViewFullRouteClick={handleViewFullRouteClick}
      chosenBusStop={chosenBusStop}
      setMessage={setMessage}
        setNeedsToLogin={setNeedsToLogin}
      />
    </div>
    </>
    }
    </div>
    )
  )
}

export default MapOverlay