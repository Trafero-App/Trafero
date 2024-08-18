import ResultItem from "./ResultItem"
import { ClipLoader } from "react-spinners"
import { IoMdSearch, IoIosCloseCircle } from "react-icons/io"
import { FaDirections } from "react-icons/fa"
import {useContext, useState, useEffect} from 'react'
import { MapContext, fetchSearchData } from "../../App"

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
// Regular expression to match two numbers (integers or floats) separated by whitespace
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

const LocationSearchBar = ({
    setChosenLocation,
    setUsingDirections
}) => {

  const [isSearchFocused,setSearchFocused] = useState(false)
  const [searchTerm,setSearchTerm] = useState('')
  const debouncedSearchTerm = useDebounce(searchTerm, 300)//300ms debounce/cooldown time
  const [searchData,setSearchData] = useState([])
  const [isSearchLoading,setSearchLoading] = useState(false)

  // handles change of input
  const handleChange = (e) => {
    setSearchLoading(true)
    setSearchTerm(e.target.value)
    setSearchData([])
  }

  //this useEffect listens to value of debouncedSearchTerm
  useEffect( () => {
    const res = extractTwoNumbers(debouncedSearchTerm)
    if(res==null){
      fetchSearchData(debouncedSearchTerm, setSearchData, setSearchLoading)//API CALL
    }
    else{
      // user inputted coordinates
      const latitude = res[0]
      const longitude = res[1]
      setSearchData([{
        properties:{
          type: 'coordinate',
          name: `${latitude} ${longitude}`
        },
        geometry:{
          coordinates:[longitude,latitude]
        }
      }])
      setSearchLoading(false)
    }
  },[debouncedSearchTerm])

  const value = useContext(MapContext)
  const {marker} = value
  const map=value.mapRef.current

  const handleResultItemClick = (data) => {
    if(!map) return;
    setSearchTerm(data.properties.name)
    map.flyTo({center: data.geometry.coordinates, zoom:  (data.properties.type=='house' || data.properties.type=='street' || data.properties.type=='coordinate') ? (data.properties.locality!=data.properties.city ? 17 : 15) : (data.properties.type=='city' || data.properties.type=='district') ? 12 : 10.5})
    marker.remove()
    if(data.properties.type=='coordinate'){
        marker.setLngLat(data.geometry.coordinates).addTo(map);
        setChosenLocation({
            name: 'Marked Location',
            type: 'marked-location',
            coordinates: data.geometry.coordinates
        })
    }  
    else{
        setChosenLocation({
            name: data.properties.name,
            type: 'poi',
            coordinates: data.geometry.coordinates
        })
    }
    setTimeout(() => {
        document.getElementById('search-bar').blur()
    },100)
  }

    return (
      
        <div 
        className={`pointer-events-auto w-full max-w-96 rounded-xl bg-white ${!isSearchFocused && 'opacity-90 hover:opacity-100'} shadow-md ${(searchTerm!='' && isSearchFocused && !isSearchLoading) && 'pb-3'}`}
        >
        <div className={`pointer-events-auto flex justify-between items-center h-14 lg:h-12 ${(searchTerm!='' && isSearchFocused) && 'border-b-2 border-gray2'}`}>
          <div className='h-14 min-w-14 lg:h-12 lg:min-w-12 flex justify-center items-center'>
            {(isSearchFocused && searchTerm!='')? 
            <IoIosCloseCircle
            className='h-8 w-8 lg:h-7 lg:w-7 text-gray4'
            style={{cursor: 'pointer'}}
            onClick={() => setSearchTerm('')}
            />
            :
            <IoMdSearch 
            className='h-8 w-8 lg:h-7 lg:w-7 text-gray4'
            style={{cursor: 'pointer'}}
            onClick={() => document.getElementById('search-bar').focus()}
            />
            }
          </div>  
          <input
          id='search-bar'
          type='text'
          value={searchTerm}
          onChange={handleChange}
          className="pl-0.5 w-full text-[18px] lg:text-[16px] rounded-xl focus:outline-none placeholder-gray4"
          placeholder="Search or click on the map"
          autoComplete="off"
          onFocus={() => setSearchFocused(true)}
          onBlur={() => {
            setTimeout(() => {
              setSearchFocused(false); // Only set to false after a delay
            }, 100); 
          }}
          />
          <div className='h-14 min-w-14 lg:h-12 lg:min-w-12 flex justify-center items-center'>
            <FaDirections 
            className='h-7 w-7 lg:h-6 lg:w-6 text-blue3 cursor-pointer'
            onClick={() => {
              setUsingDirections(true)
            }}
            />
          </div>
          
        </div>
        {(searchTerm!='' && isSearchFocused) && 
        (isSearchLoading ? 
        <div className='pointer-events-auto flex justify-center items-center py-4'>
          <ClipLoader size='29px' color='#C8C8C8'/>
        </div> 
        : searchData.length==0 ? 
        <h1 className='pointer-events-auto flex justify-center items-center text-sm h-10 lg:h-8 text-gray4 mt-2'>No results were found.</h1> 
        :
          (isSearchFocused &&
          <div className={`${searchData.length>3 && 'scrollable h-36'} pointer-events-auto mt-3`}>
            {searchData.map((element,index) => <ResultItem key={index} data={element} handleResultItemClick={handleResultItemClick}/>)}
          </div>
          )
        )}
      </div>
    )
}

export default LocationSearchBar