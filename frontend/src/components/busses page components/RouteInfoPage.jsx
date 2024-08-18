import { useContext,useEffect, useState } from 'react';
import {useParams, useNavigate} from 'react-router-dom';
import { MapContext } from '../../App';
import axios from 'axios'
import { ClipLoader } from 'react-spinners';
import {IoIosArrowBack, IoMdStarOutline, IoMdStar} from 'react-icons/io'
import {TbCopy, TbPlus} from 'react-icons/tb'

const minutesToText= (minutes) => {
    if(minutes==0) return '0m'
    if(minutes%60==0) return `${Math.floor(minutes/60)}h`
    if(minutes<60) return `${minutes}m`
    return `${Math.floor(minutes/60)}h ${minutes%60}m`
}

const RouteInfoPage = () => {

    const value = useContext(MapContext)
    const [needsToLogin, setNeedsToLogin] = useState(false)
    const [message, setMessage] = useState('')
    const {savedRoutes, setSavedRoutes, isLoggedIn} = value
    const navigate = useNavigate()
    
    const [routeExists, setRouteExists] = useState(true)
    const [dataLoading, setDataLoading] = useState(true)
    const [data, setData] = useState(null)
    const [item, setItem] = useState(null)

    //fetches info on route (has been changed)
    const fetchRouteInfo = async (route_id) => {
        await axios.get(`/api/route_details/${route_id}`,{
        headers: {
            'Content-Type': 'application/json'
        }
        })
        .then((res) => {
            if(res.status==200){
                setRouteExists(true)
                const routeInfo = res.data.route_data
                setData(routeInfo)
                setItem({
                    route_id: routeInfo.route_id,
                    route_name: routeInfo.route_name,
                    description: routeInfo.description,
                    line: routeInfo.line
                })
                setDataLoading(false)
            }
        })
        .catch((e) => {
            if(e.response.status==404 || e.response.status==422){
                setRouteExists(false)
                setDataLoading(false)
            }
        })
    }

    const {id}= useParams()
    //runs on render and fetches info abt route
    useEffect(() => {
        setData(null)
        setRouteExists(false)
        setDataLoading(true)
        fetchRouteInfo(id)
    },[id])

    const {setChosenRoute, setChosenRouteLoading, setChosenRouteIntervalId, fetchRouteData, setChosenBusIds, setSingleChosenBusId, userType, routes, setRoutes} = useContext(MapContext)
    const handleViewOnMapClick = () => {
        setChosenRoute(null)
        navigate('/map')
        //wait 100 ms so effects of setting chosen route to null happen
        setTimeout(() => {
            setSingleChosenBusId(null)
            setChosenBusIds(null)
            setChosenRouteLoading(true)
            fetchRouteData(id)
            setChosenRouteIntervalId(setInterval(() => {
                fetchRouteData(id)
            },2000))
        },100) 
    }

    //copies link to current clipboard (to be changed)
    const copyLinkToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(`http://localhost:3000/search/route/${id}`);
        }
        catch(e){}
    }

    //handles click of favorite
    const favoriteClick = () => {
        if(isLoggedIn){
          if(savedRoutes.filter((e) => e.route_id==data.route_id).length==0){
            setSavedRoutes([{route_id: data.route_id, route_name: data.route_name, description: data.description}].concat(savedRoutes))
          }
          else{
            setSavedRoutes(savedRoutes.filter((e) => e.route_id!=data.route_id))
          }
        }
        else{
          setMessage('You must be logged in to add a route to Favorites')
          setNeedsToLogin(true)
        }
    }

    return (
        needsToLogin ?
        <div className='w-full flex justify-center items-center backdrop-blur-sm p-3'>
            <div className='w-full max-w-80 rounded-xl bg-white shadow-md'>
                <div className='w-full h-32 p-6 flex justify-center items-center'>
                    <h1 className='font-medium'>{message}</h1>
                </div>
                <div className='px-6 pb-6 flex items-center justify-between'>
                    <div 
                    className='mr-1.5 h-10 w-full bg-blue3 rounded-xl cursor-pointer flex justify-center items-center'
                    onClick={() => {navigate('/settings');}}
                    >
                        <h1 className='text-white'>Go to Settings</h1>
                    </div>
                    <div 
                    className='ml-1.5 h-10 w-full border-2 border-gray1 rounded-xl hover:bg-gray1 transition duration-200 cursor-pointer flex justify-center items-center'
                    onClick={() => {
                        setNeedsToLogin(false)
                    }
                    }
                    >
                        <h1>Cancel</h1>
                    </div>
                </div>     
            </div>
        </div>
        :
        <div className='w-full h-full flex justify-center items-center backdrop-blur-sm p-3'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md max-h-full flex flex-col'>
                {
                dataLoading ?
                //data is being fetched
                <div 
                className='h-full flex flex-col justify-between'>
                    <div
                    className='md:hidden text-gray4 flex h-14 items-center cursor-pointer right-shadow'
                    onClick={() => navigate('/search')}
                    >
                        <div className='h-14 w-14 flex justify-center items-center'>
                            <IoIosArrowBack className='w-8 h-8'/>
                        </div>
                        <h1 className='text-[18px]'>Back to Search</h1>
                    </div>
                    <div className='flex h-96 justify-center items-center'>
                        <ClipLoader size='29px' color='#C8C8C8'/>
                    </div>
                    <div className='md:hidden h-14'/>
                </div>
                :
                routeExists ?
                //route with this ID exists
                <>
                    <div 
                    className='md:hidden text-gray4 flex h-14 items-center cursor-pointer border-b-2 border-gray2'
                    onClick={() => navigate('/search')}
                    >
                        <div className='h-14 w-14 flex justify-center items-center'>
                            <IoIosArrowBack className='w-8 h-8'/>
                        </div>
                        <h1 className='text-[18px]'>Back to Search</h1>
                    </div>
                    <div className='flex-grow h-full overflow-auto scrollable'>
                        <div className='flex justify-between items-center border-b-2 border-gray2'>
                            <h1 className='font-bold text-2xl p-4'>{data.route_name}</h1>
                            <div 
                            className='h-8 w-8 flex justify-center items-center mr-4 cursor-pointer'
                            onClick={favoriteClick}
                            >
                                {savedRoutes.filter((e) => e.route_id==data.route_id).length==0 ?
                                <IoMdStarOutline className='h-8 w-8 text-gray2  hover:text-gray4 transition duration-200'/>
                                :
                                <IoMdStar className='h-8 w-8 text-gray2  hover:text-gray4 transition duration-200'/>
                                }
                                
                            </div>
                        </div>
                        <h1 className='px-4 pb-1 pt-3'><span className='font-semibold'>Route Type:</span> {data.route_type}</h1>
                        <h1 className='px-4 pb-1'><span className='font-semibold'>Description:</span> {data.description}</h1>
                        <h1 className='px-4 pb-1'><span className='font-semibold'>Distance:</span> {data.distance}</h1>
                        <h1 className='px-4 pb-3'><span className='font-semibold'>Estimated travel time:</span> {minutesToText(data.estimated_travel_time)}</h1>
                        <h1 className='px-4 pb-1 pt-3 border-t-2 border-gray2'><span className='font-semibold'>Working hours:</span> {data.working_hours}</h1>
                        <h1 className='px-4 pb-1'><span className='font-semibold'>Active days:</span> {data.active_days}</h1>
                        <h1 className='px-4 pb-3'><span className='font-semibold'>Expected price:</span> {data.expected_price}</h1>
                        <h1 className='px-4 pb-1 pt-3 border-t-2 font-semibold'>Contact Information:</h1>
                        <h1 className='px-4 pb-1'><span className='font-semibold'>Company Name:</span> {data.company_name}</h1>
                        <h1 className='px-4 pb-3'><span className='font-semibold'>Phone Number:</span> {data.phone_number}</h1>
                    </div>
                    <div className='flex justify-between items-center border-t-2 border-gray2 h-fit'>
                        <div className='ml-4 h-12 w-12 flex justify-center items-center'>
                            {
                            userType=='driver' &&
                            <TbPlus
                            //route.includes(item) => routes.filter( e => JSON.stringify(e)==JSON.stringify(item)).length!=0 because js compares references
                            className={`h-7 w-7 ${routes.filter( e => JSON.stringify(e)==JSON.stringify(item)).length!=0 ? '' :'text-gray2 hover:text-gray4 cursor-pointer'} transition duration-200`}
                            onClick={() => {
                                if(routes.filter( e => JSON.stringify(e)==JSON.stringify(item)).length==0){
                                    setRoutes(routes.concat([item]))
                                }
                            }}
                            />
                            }
                        </div>
                        <div 
                        className='flex my-4 justify-center items-center rounded-xl border-2 border-gray1 w-full h-12 max-w-[10.5rem] cursor-pointer hover:bg-gray1 transition duration-200'
                        onClick={handleViewOnMapClick}
                        >
                            <h1>View on map</h1>
                        </div>
                        <div className='mr-4 h-12 w-12 flex justify-center items-center'>
                            <TbCopy
                            className='h-7 w-7 text-gray2 hover:text-gray4 transition duration-200 cursor-pointer'
                            onClick={copyLinkToClipboard}
                            />
                        </div>
                    </div>
                </>
                :
                //route with this ID doesn't exist
                <div className='h-full flex flex-col justify-between'>
                    <div 
                    className='md:hidden text-gray4 flex h-14 items-center cursor-pointer'
                    onClick={() => navigate('/search')}
                    >
                        <div className='h-14 w-14 flex justify-center items-center'>
                            <IoIosArrowBack className='w-8 h-8'/>
                        </div>
                        <h1 className='text-[18px]'>Back to Search</h1>
                    </div>
                    <div className='flex h-96 justify-center items-center'>
                        <h1 className='text-xl font-semibold'>This route doesn't exist.</h1>
                    </div>
                    <div className='md:hidden h-14'/>
                </div>
                }
            </div>
        </div>
    )
}

export default RouteInfoPage