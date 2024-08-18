import { useState, useEffect } from "react"
import axios from 'axios'
import {Outlet, useLocation, useNavigate} from 'react-router-dom';
import { ClipLoader } from "react-spinners";
import {IoBookmarkOutline} from 'react-icons/io5'
import RouteHistoryItem from "../busses page components/RouteHistoryItem"
import BusHistoryItem from '../busses page components/BusHistoryItem'
import BusResultItem from "../busses page components/BusResultItem";
import RouteResultItem from '../busses page components/RouteResultItem'

function fix(str) {
    if (/[a-zA-Z]/.test(str[0]) && (str.length==1 || str[1]!=' ')) {
      return str.slice(0, 1) + ' ' + str.slice(1);
    } else {
      return str;
    }
  }

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

const BussesPage = () => {

    const navigate = useNavigate()
    const location = useLocation()
    const [isOnInfoPage, setOnInfoPage] = useState(true)
    useEffect(() => {
        setOnInfoPage(location.pathname!='/search')
    },[location.pathname])

    const [routesHistory, setRoutesHistory] = useState([])
    useEffect(() => {
        setRoutesHistory(JSON.parse(localStorage.getItem('routes-history')))
    },[localStorage.getItem('routes-history')])

    const [bussesHistory, setBussesHistory] = useState([])
    useEffect(() => {
        setBussesHistory(JSON.parse(localStorage.getItem('busses-history')))
    },[localStorage.getItem('busses-history')])

    //determines what we're searching for
    const [searchType, setSearchType] = useState('busses')

    const [routesSearchTerm, setRoutesSearchTerm] = useState('')
    const debouncedRoutesSearchTerm = useDebounce(routesSearchTerm,350)
    const [routesSearchData, setRoutesSearchData] = useState(null)
    const [routesSearchDataLoading, setRoutesSearchDataLoading] = useState(false)

    const [bussesSearchTerm, setBussesSearchTerm] = useState('')
    const debouncedBussesSearchTerm = useDebounce(bussesSearchTerm,350)
    const [bussesSearchData, setBussesSearchData] = useState(null)
    const [bussesSearchDataLoading, setBussesSearchDataLoading] = useState(false)

    //fetches routes based on search term (has been changed)
    const fetchRoutes = async (query) => {
        await axios.get(`/api/search_routes/${query}`,{
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res) => {
            if(res.status==200){
                setRoutesSearchData(res.data.routes)
                setRoutesSearchDataLoading(false)
            }
        })
    }
    
    //fetches busses based on license plate(to be changed)
    const fetchBusses = async (query) => {
        await axios.get(`/api/search_vehicles/${query}`,{
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then((res) => {
            if(res.status==200){
                setBussesSearchData(res.data.vehicles)
                setBussesSearchDataLoading(false)
            }
        })
    }

    //listens to value of debouncedRoutesSearchTerm and fetches data
    useEffect(() => {
        if(debouncedRoutesSearchTerm==''){
            setRoutesSearchDataLoading(false)
            setRoutesSearchData(null)
        }
        else{
            fetchRoutes(debouncedRoutesSearchTerm)
        }
        
    },[debouncedRoutesSearchTerm])
    //listens to value of debouncedBussesSearchTerm and fetches data
    useEffect(() => {
        if(debouncedBussesSearchTerm==''){
            setBussesSearchDataLoading(false)
            setBussesSearchData(null)
        }
        else{
            fetchBusses(fix(debouncedBussesSearchTerm))
        }
        
    },[debouncedBussesSearchTerm])

    return (
        <div className={`absolute z-20 w-full h-screen flex pointer-events-auto border-b-[64px] md:border-b-[56px] md:pr-0 backdrop-blur-sm ${!isOnInfoPage && 'justify-center md:justify-normal'}`}>
            <div className={`${isOnInfoPage && 'hidden md:flex'} m-3 bg-white w-full max-w-[25.5rem] flex flex-col items-center rounded-[1rem] shadow-md`}>
                <div className='flex justify-between items-center w-full p-6 pb-4'>
                    <div className='h-10 w-10'/>
                    <h1 className='text-xl font-bold'>Search</h1>
                    <div className='flex justify-center items-center'>
                        <div 
                        className='flex justify-center items-center h-10 w-10 rounded-[2rem] text-gray2 hover:text-gray4 transition duration-200 cursor-pointer'
                        onClick={() => navigate('/saved')}
                        >
                            <IoBookmarkOutline 
                            className='h-6 w-6'
                            />
                        </div>
                    </div>
                </div>
                <div className='flex justify-between w-full pb-6'>
                    <div 
                    className={`${searchType=='busses' ?  'bg-blue3 hover:bg-blue4 text-white' :'border-2 border-gray1 hover:bg-gray1'} mr-1.5 ml-6 flex justify-center items-center rounded-xl h-10 w-full max-w-50% cursor-pointer transition duration-200`}
                    onClick={() => setSearchType('busses')}
                    >
                        <h1>Busses</h1>
                    </div>
                    <div 
                    className={`${searchType=='routes' ?  'bg-blue3 hover:bg-blue4 text-white' :'border-2 border-gray1 hover:bg-gray1'} ml-1.5 mr-6 flex justify-center items-center rounded-xl h-10 w-full max-w-50% cursor-pointer transition duration-200`}
                    onClick={() => setSearchType('routes')}
                    >
                        <h1>Routes</h1>
                    </div>   
                </div>
                <div className="px-6 w-full pt-3 border-t-2 border-gray1">
                    <input
                    autoComplete="off"
                    id='search-bar'
                    value={searchType=='routes' ? routesSearchTerm : bussesSearchTerm}
                    onChange={(e) => {
                        if(searchType=='routes'){
                            setRoutesSearchDataLoading(true)
                            setRoutesSearchTerm(e.target.value)
                            setRoutesSearchData(null)
                            if(e.target.value=='') setRoutesSearchDataLoading(false)
                        }
                        else{
                            setBussesSearchDataLoading(true)
                            setBussesSearchTerm(e.target.value)
                            setBussesSearchData(null)
                            if(e.target.value=='') setBussesSearchDataLoading(false)
                        }
                    }}
                    className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                    placeholder={searchType=='routes' ? 'Search routes by name or description' : 'Search busses by license plate'}
                    /> 
                </div>
                
                {searchType=='routes' ?
                //routes section
                (!routesSearchDataLoading && routesSearchTerm=='') ?
                //nothing is being searched 
                routesHistory.length==0 ?
                <div className='w-full h-12 mt-3 flex justify-center items-center'>
                    <h1 className='font-semibold'>No recently visited routes</h1>
                </div>
                :
                <div className='w-full scrollable overflow-auto my-3 h-full'>
                    {routesHistory.map((element,index) => 
                    <RouteHistoryItem 
                    key={index} 
                    item={element}
                    setRoutesHistory={setRoutesHistory}
                    />
                    )}
                </div>
                :
                //we're searching for routes
                (
                routesSearchDataLoading || !routesSearchData ?
                //routes are loading
                <div className='flex justify-center items-center h-12 mt-3'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                :
                // we got search results back
                routesSearchData.length==0 ?
                <div className='w-full h-12 mt-3 flex justify-center items-center'>
                    <h1 className='font-semibold'>No results found.</h1>
                </div>
                :
                <div className='w-full scrollable overflow-auto my-3 h-full'>
                    {routesSearchData.map((element,index) => <RouteResultItem key={index} route={element}/>)}
                </div>
                )
                :
                //busses section
                (!bussesSearchDataLoading && bussesSearchTerm=='') ?
                //nothing is being searched for
                bussesHistory.length==0 ?
                <div className='w-full h-12 mt-3 flex justify-center items-center'>
                    <h1 className='font-semibold'>No recently visited busses</h1>
                </div>
                :
                <div className='w-full scrollable overflow-auto my-3 h-full'>
                    {bussesHistory.map((element,index) => 
                    <BusHistoryItem 
                    key={index} 
                    item={element}
                    setBussesHistory={setBussesHistory}
                    />
                    )}
                </div>
                :
                //we're searching for busses
                bussesSearchDataLoading || !bussesSearchData ?
                //busses are loading
                <div className='flex justify-center items-center h-12 mt-3'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                :
                // we got search results back
                bussesSearchData.length==0 ?
                <div className='w-full h-12 mt-3 flex justify-center items-center'>
                    <h1 className='font-semibold'>No results found.</h1>
                </div>
                :
                <div className='w-full scrollable overflow-auto my-3 h-full'>
                    {bussesSearchData.map((element,index) => <BusResultItem key={index} vehicle={element}/>)}
                </div>
                }
            </div>
            <Outlet/>
        </div>
    )
}

export default BussesPage