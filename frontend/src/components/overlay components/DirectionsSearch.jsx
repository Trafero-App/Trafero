import { IoIosArrowBack, IoIosCloseCircle, IoMdLocate } from "react-icons/io"
import {LuArrowUpDown} from 'react-icons/lu'
import { useState, useEffect, useContext, useRef } from "react"
import { fetchSearchData } from "../../App"
import { ClipLoader } from "react-spinners"
import ResultItem from "./ResultItem"
import { MapContext } from "../../App"

const useDebounce = (value,delay) => {// TODO : understand wtf this is
    const [debouncedSearchTerm,setDebouncedSearchTerm] = useState('')
    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedSearchTerm(value)
      }, delay)
  
      return () => {
        clearTimeout(handler)
      }
    },[value,delay]) 
    return debouncedSearchTerm
}
  
function extractTwoNumbers(str) {
    // Regular expression to match two numbers (integers or floats)
    const regex = /^(-?\d+(\.\d+)?)[, ]\s*(-?\d+(\.\d+)?)\s*$/;
    const match = str.match(regex);
    
    if (match) {
      // The first and second numbers are captured in groups 1 and 3
      const num1 = parseFloat(match[1]);
      const num2 = parseFloat(match[3]);
      return [num1, num2];
    } else {
      // Return null if the string does not match the pattern
      return null;
    }
}

const DirectionsSearch = ({
    setUsingDirections,
    setSharingLocation, liveLocation,
    startingPoint, setStartingPoint,
    destination, setDestination,
    handleSearchRoutesClick
}) => {
    const value = useContext(MapContext)
    const {startMarker, destinationMarker, isMapLoaded} = value
    const map = value.mapRef.current

    const [isStartSearchFocused, setStartSearchFocused] = useState(false)
    const [startSearchTerm, setStartSearchTerm] = useState('')
    const [isStartSearchLoading, setStartSearchLoading] = useState(false)
    const [startSearchData, setStartSearchData] = useState(null)
    const debouncedStartSearchTerm = useDebounce(startSearchTerm, 300)

    const [isDestinationSearchFocused, setDestinationSearchFocused] = useState(false)
    const [destinationSearchTerm, setDestinationSearchTerm] = useState('')
    const [isDestinationSearchLoading, setDestinationSearchLoading] = useState(false)
    const [destinationSearchData, setDestinationSearchData] = useState(null)
    const debouncedDestinationSearchTerm = useDebounce(destinationSearchTerm, 300)

    const startingPointRef = useRef(startingPoint)
    const destinationRef = useRef(destination)

    //this useEffect listens to value of debouncedStartSearchTerm
    useEffect( () => {
        const res = extractTwoNumbers(debouncedStartSearchTerm)
        if(res==null){
        fetchSearchData(debouncedStartSearchTerm,setStartSearchData, setStartSearchLoading)//API CALL
        }
        else{
        // user inputted coordinates
        const latitude = res[0]
        const longitude = res[1]
        setStartSearchData([{
            properties:{
            type: 'coordinate',
            name: `${latitude} ${longitude}`
            },
            geometry:{
            coordinates:[longitude,latitude]
            }
        }])
        setStartSearchLoading(false)
        }
    },[debouncedStartSearchTerm])

    //this useEffect listens to value of debouncedDestinationSearchTerm
    useEffect( () => {
        const res = extractTwoNumbers(debouncedDestinationSearchTerm)
        if(res==null){
        fetchSearchData(debouncedDestinationSearchTerm,setDestinationSearchData, setDestinationSearchLoading)//API CALL
        }
        else{
        // user inputted coordinates
        const latitude = res[0]
        const longitude = res[1]
        setDestinationSearchData([{
            properties:{
            type: 'coordinate',
            name: `${latitude} ${longitude}`
            },
            geometry:{
            coordinates:[longitude,latitude]
            }
        }])
        setDestinationSearchLoading(false)
        }
    },[debouncedDestinationSearchTerm])

    //updates refs and pans camera when both are selected
    useEffect(() => {
        destinationRef.current=destination
        startingPointRef.current=startingPoint
        if(startingPoint && destination){
            const point1 = startingPoint.coordinates
            const point2 = destination.coordinates
            const bounds = [point1, point2]
            map.fitBounds(bounds,{padding: 100})
        }
    },[startingPoint, destination])

    //function that returns a functions that uses given setter to choose location as ...
    const handleResultItemClick = (set) => {
        return (data) => {
            set({
                name: data.properties.name,
                coordinates: data.geometry.coordinates
            })
        }
    }

    const handleSwitch = () => {
        const oldStart = startingPointRef.current
        const oldDestination = destinationRef.current
        if(document.getElementById('destination-marker')){
            document.getElementById('destination-marker').remove()
        }
        if(document.getElementById('start-marker')){
            document.getElementById('start-marker').remove()
        }
        if(oldStart && oldStart.isMarkedLocation){
            destinationMarker.remove()
            destinationMarker.setLngLat(oldStart.coordinates).addTo(map)
        }
        if(oldDestination && oldDestination.isMarkedLocation){
            startMarker.remove()
            startMarker.setLngLat(oldDestination.coordinates).addTo(map)
        }
        setStartingPoint(oldDestination)
        setDestination(oldStart)
    }

    return (
        <div 
        className='pointer-events-auto w-full max-w-96 rounded-xl bg-white shadow-md'
        >
            <div 
            className='text-gray4 flex items-center h-14 lg:h-12 border-b-2 border-gray2'
            style={{cursor: 'pointer'}}
            onClick={() => setUsingDirections(false)}
            >
                <IoIosArrowBack
                className='mx-2 h-8 w-8 lg:h-7 lg:w-7 text-gray4'
                />
                <h1 className='text-[18px] lg:text-[16px]'>Back to Search</h1>
            </div>
            <div className='flex justify-between p-3 pr-0'>
                <div className='w-full'>
                    {!startingPoint ?
                    <div className='w-full flex bg-gray1 rounded-lg'>
                        <input
                        id='start-search-bar'
                        className='h-10 w-full focus:outline-none pl-3 bg-gray1 rounded-lg placeholder-gray4'
                        placeholder='Choose starting point or click on the map'
                        onChange={(e) => {
                            setStartSearchLoading(true)
                            setStartSearchTerm(e.target.value)
                            setStartSearchData([])
                        }}
                        autoComplete="off"
                        onFocus={() => setStartSearchFocused(true)}
                        onBlur={() => 
                            setTimeout(() => {
                                setStartSearchFocused(false)
                            },100)
                        }
                        />
                        <div className='w-10 h-10 flex justify-center items-center'>
                            <IoMdLocate 
                            className='w-5 h-5 cursor-pointer text-gray4'
                            onClick={() => {
                                if(isMapLoaded){
                                    if(liveLocation){
                                        setStartingPoint({
                                            name: 'Current Location',
                                            coordinates: liveLocation
                                        })
                                    }
                                    else{
                                        setSharingLocation(true)
                                    }
                                }
                            }}
                            />
                        </div>
                    </div>
                    :
                    <div className='h-10 w-full pl-3 bg-gray1 border-2 border-gray4 rounded-lg flex justify-between items-center'>
                        <h1>{startingPoint.name}</h1>
                        <div className='flex justify-center items-center h-10 w-10'>
                            <IoIosCloseCircle 
                            className='h-7 w-7 cursor-pointer text-gray4'
                            onClick={() => setStartingPoint(null)}
                            />
                        </div>
                    </div>
                    }
                    {!destination ?
                    <div className='w-full flex bg-gray1 rounded-lg mt-3'>
                        <input
                        id='destination-search-bar'
                        className='h-10 w-full focus:outline-none pl-3 bg-gray1 rounded-lg placeholder-gray4'
                        placeholder={!startingPoint ? 'Choose destination' : 'Choose destination or click on the map'}
                        onChange={(e) => {
                            setDestinationSearchLoading(true)
                            setDestinationSearchTerm(e.target.value)
                            setDestinationSearchData([])
                        }}
                        autoComplete="off"
                        onFocus={() => setDestinationSearchFocused(true)}
                        onBlur={() => 
                            setTimeout(() => {
                                setDestinationSearchFocused(false)
                            },100)
                        }
                        />
                        <div className='w-10 h-10 flex justify-center items-center'>
                            <IoMdLocate 
                            className='w-5 h-5 cursor-pointer text-gray4'
                            onClick={() => {
                                if(isMapLoaded){
                                    if(liveLocation){
                                        setDestination({
                                            name: 'Current Location',
                                            coordinates: liveLocation
                                        })
                                    }
                                    else{
                                        setSharingLocation(true)
                                    }
                                }
                            }}
                            />
                        </div>
                    </div>
                    :
                    <div className='mt-3 h-10 w-full pl-3 bg-gray1 border-2 border-gray4 rounded-lg flex justify-between items-center'>
                        <h1>{destination.name}</h1>
                        <div className='flex justify-center items-center h-10 w-10'>
                            <IoIosCloseCircle 
                            className='h-7 w-7 cursor-pointer text-gray4'
                            onClick={() => setDestination(null)}
                            />
                        </div>
                    </div>
                    }
                </div> 
                <div className='flex justify-center items-center px-3'>
                    <LuArrowUpDown 
                    className='h-6 w-6 text-gray2 hover:text-gray4 transition duration-200 cursor-pointer'
                    onClick={handleSwitch}
                    />
                </div>   
            </div>
            {(startSearchTerm!='' && isStartSearchFocused) && 
            <div className='py-3 border-t-2 border-gray2'>
                {isStartSearchLoading ?
                <div className='flex justify-center'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                :
                startSearchData.length==0 ?
                <div className='h-[29px] flex justify-center items-center'>
                    <h1 className='text-gray4 text-md'>No results found.</h1>
                </div>
                :
                <div className={startSearchData.length>2 && 'h-24 scrollable'}>
                    {startSearchData.map((element,index) => <ResultItem key={index} data={element} handleResultItemClick={handleResultItemClick(setStartingPoint)}/>)}
                </div>
                }
            </div>
            }
            {(destinationSearchTerm!='' && isDestinationSearchFocused) && 
            <div className='py-3 border-t-2 border-gray2'>
                {isDestinationSearchLoading ?
                <div className='flex justify-center'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                :
                destinationSearchData.length==0 ?
                <div className='h-[29px] flex justify-center items-center'>
                    <h1 className='text-gray4 text-md'>No results found.</h1>
                </div>
                :
                <div className={destinationSearchData.length>2 && 'h-24 scrollable'}>
                    {destinationSearchData.map((element,index) => <ResultItem key={index} data={element} handleResultItemClick={handleResultItemClick(setDestination)}/>)}
                </div>
                }
            </div>
            }
            {(startingPoint && destination) &&
            <div className='flex mb-3 justify-center'>
                <div 
                className='h-10 w-44 flex justify-center items-center rounded-xl bg-blue3 hover:bg-blue4 transition duration-200 cursor-pointer'
                onClick={() => handleSearchRoutesClick(startingPoint,destination)}
                >
                    <h1 className='text-md text-white'>Search Routes</h1>
                </div>
            </div>
            }
        </div>
    )
}

export default DirectionsSearch