import { useContext,useEffect, useState } from 'react';
import {useParams, useNavigate} from 'react-router-dom';
import { MapContext } from '../../App';
import axios from 'axios';
import { ClipLoader } from 'react-spinners';
import {IoIosArrowBack, IoIosArrowDown, IoIosArrowUp, IoMdStarOutline,IoMdStar, IoMdThumbsDown, IoMdThumbsUp, IoMdClose} from 'react-icons/io'
import {TbCopy} from 'react-icons/tb'
import { MdCheckBox , MdCheckBoxOutlineBlank} from 'react-icons/md';
import GiveNicknamePrompt from '../GiveNicknamePrompt';

const capitalizeFirstLetter = (str) => {
    if (!str) return str;
    return str.charAt(0).match(/[a-zA-Z]/) ? str.charAt(0).toUpperCase() + str.slice(1) : str;
};

const BusInfoPage = () => {

    //navigates back to search area
    const navigate = useNavigate()
    
    const [needsToLogin, setNeedsToLogin] = useState(false)
    const [message, setMessage] = useState('')
    const [needsToGiveNickname, setNeedsToGiveNickname] = useState(false)

    const [busExists, setBusExists] = useState(true)
    const [dataLoading, setDataLoading] = useState(true)
    const [data, setData] = useState(null)

    const [isShowingComplaints, setShowingComplaints] = useState(false)
    const [isOnDislikeForm, setOnDislikeForm] = useState(false)

    const [isSelected1, setSelected1] = useState(false)
    const [isSelected2, setSelected2] = useState(false)
    const [isSelected3, setSelected3] = useState(false)
    const [isSelected4, setSelected4] = useState(false)
    const [isSelected5, setSelected5] = useState(false)
    const [isSelected6, setSelected6] = useState(false)
    const [isSelected7, setSelected7] = useState(false)
    const [isSelected8, setSelected8] = useState(false)
    const [writtenReview, setWrittenReview] = useState('')

    const value = useContext(MapContext)
    const {authenticationToken, isLoggedIn, userType} = value
    const {savedVehicles, setSavedVehicles} = value
    const map = value.mapRef.current

    const accessToken = localStorage.getItem('authentication-token') ? localStorage.getItem('authentication-token') : authenticationToken

    //fetches info on bus (to be changed)
    const fetchBusInfo= async (id) => {
        //if info doesnt exist, clearInterval(interval)
        await axios.get(`/api/vehicle/${id}`,{
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': accessToken!='' ? `Bearer ${accessToken}` : null
                }
            }
        )
        .then((res) => {
            if(res.status==200){
                setBusExists(true)
                setData(res.data.content)
                setDataLoading(false)
            }
        })
        .catch((e) => {
            if(e.response.status==404 || e.response.status==422){
                setBusExists(false)
                setDataLoading(false)
            }
        })
    }

    //tells API that we added a like to this vehicle and gets new data(to be changed)
    const like = async (id) => {
        if(accessToken!=''){
            await axios({
                method: !data.user_choice ? 'post' : 'put',
                url: '/api/feedback',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authenticationToken}`
                },
                data: {
                    reaction: 'thumbs_up',
                    vehicle_id: id
                }
            })
            .then((res) => {
                if(res.status==200){
                    data.user_choice='thumbs_up'
                }
                fetchBusInfo(id)
            })
        }
    }
    const dislike = async (id) => {
        var complaints = []
        if(isSelected1) complaints.push('drives too slow')
        if(isSelected2) complaints.push('reckless')
        if(isSelected3) complaints.push('rude behavior')
        if(isSelected4) complaints.push('uncomfortable')
        if(isSelected5) complaints.push('bad condition')
        if(isSelected6) complaints.push('unpleasant smell')
        if(isSelected7) complaints.push('waits too much')
        if(isSelected8 || writtenReview!='') complaints.push('other')
        if(writtenReview!='') complaints.push(writtenReview)
        await axios({
            method: !data.user_choice ? 'post' : 'put',
            url: `/api/feedback`,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            data: {
                reaction: 'thumbs_down',
                vehicle_id: id,
                complaints: complaints,
            }
        })
        .then((res) => {
            if(res.status==200){
                data.user_choice='thumbs_down'
            }
            fetchBusInfo(id)
            setOnDislikeForm(false)
        })
    }
    //tells API that we removed like from this vehicle and gets new data (to be changed)
    const removeReaction = async (id) => {
        if(accessToken!=''){
            await axios({
                method:'DELETE',
                url: `/api/feedback/${id}`,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            })
            .then((res) => {
                if(res.status==200){
                    data.user_choice==null
                }
                fetchBusInfo(id)
            })
        }
        
    }

    const {id}= useParams()
    //runs everytime id changes and starts fetching info abt bus
    useEffect(() => {
        setData(null)
        setDataLoading(true)
        setBusExists(false)
        fetchBusInfo(id)
    },[id])

    //takes user to the map and pans it to the vehicle's location
    const handleViewOnMap = () => {
        map.flyTo({center: data.coordinates, zoom: 14})
        navigate('/map')
    }

    //copies link to current clipboard (to be changed)
    const copyLinkToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(`http://localhost:3000/search/bus/${id}`);
        }
        catch(e){}
    }

    //handles click of like button (to be changed)
    const handleLikeClick = () => {
        if(isLoggedIn){
            if(userType=='passenger'){
                if(data.user_choice=='thumbs_up'){
                    removeReaction(id)
                }
                else{
                    like(id)
                }
            }
            else{
                setMessage('You cannot leave a review as a driver')
                setNeedsToLogin(true)
            }
        }
        else{
            setMessage('You must be logged in to leave a review')
            setNeedsToLogin(true)
        }
    }

    //handles click of dislike button
    const handleDislikeClick = () => {
        if(isLoggedIn){
            if(userType=='passenger'){
                if(data.user_choice=='thumbs_down'){
                    removeReaction(id)
                }
                else{
                    setOnDislikeForm(true)
                }
            }
            else{
                setMessage('You cannot leave a review as a driver')
                setNeedsToLogin(true)
            }
        }
        else{
            setMessage('You must be logged in to leave a review')
            setNeedsToLogin(true)
        }
    }
      
    //handles click of favorite
    const favoriteClick = () => {
        if(isLoggedIn){
          if(savedVehicles.filter((e) => e.id==data.id).length==0){
            setNeedsToGiveNickname(true)
          }
          else{
            setSavedVehicles(savedVehicles.filter((e) => e.id!=data.id))
          }
        }
        else{
          setMessage('You must be logged in to add a vehicle to Favorites')
          setNeedsToLogin(true)
        }
    }

    return (
        <>
        {
        isOnDislikeForm &&
        <div className='z-50 fixed pointer-events-auto h-screen w-screen flex justify-center items-center backdrop-blur-sm bg-gray5 bg-opacity-40 p-3 border-b-[64px] md:border-b-[56px]'>
            <div className='bg-white w-full max-w-[30rem] rounded-xl shadow-md max-h-full'>
                <div className='flex justify-between items-center'>
                    <h1 className='font-semibold pl-5 my-2'>Choose any of the below complaints</h1>
                    <div className='h-14 w-14 flex justify-center items-center'>
                        <div 
                        className='h-9 w-9 rounded-[2rem] flex justify-center items-center cursor-pointer hover:bg-gray1 transition duration-200'
                        onClick={() => {setOnDislikeForm(false)}}
                        >
                            <IoMdClose className='h-6 w-6'/>
                        </div>
                    </div>
                </div>
                <div className='scrollable overflow-auto h-fit'>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected1(!isSelected1)}
                        >
                            {isSelected1 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Drives too slow</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected2(!isSelected2)}
                        >
                            {isSelected2 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Reckless driving (abrupt stops, drives too fast…)</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected3(!isSelected3)}
                        >
                            {isSelected3 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Rude behavior</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected4(!isSelected4)}
                        >
                            {isSelected4 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Uncomfortable seats or overcrowded conditions</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected5(!isSelected5)}
                        >
                            {isSelected5 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Vehicle in bad condition</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected6(!isSelected6)}
                        >
                            {isSelected6 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Unpleasant smell (allows smoking or other reasons)</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected7(!isSelected7)}
                        >
                            {isSelected7 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Waits too much time to fill up, stationary for too long</h1>
                    </div>
                    <div className='flex mb-2 mx-5'>
                        <div 
                        className='cursor-pointer mr-2'
                        onClick={() => setSelected8(!isSelected8)}
                        >
                            {isSelected8 ?
                            <MdCheckBox size='24px'/>
                            :
                            <MdCheckBoxOutlineBlank size='24px'/>
                            }
                        </div>
                        <h1>Other</h1>
                    </div>
                    <div className='w-full px-5'>
                        <textarea
                        value={writtenReview}
                        onChange={(e) => setWrittenReview(e.target.value)}
                        type='text'
                        className='resize-none w-full h-30 min-h-30 border-0 focus:outline-none p-3 bg-gray1 rounded-lg placeholder-gray4'
                        placeholder="You can also write a detailed review (won't be visible to other users)"
                        />
                    </div>
                </div>
                <div className='flex justify-center pb-5 pt-4'>
                    <div 
                    className='w-full h-12 max-w-[10.5rem] flex justify-center items-center border-2 border-gray1 rounded-xl hover:bg-gray1 transition duration-200'
                    style={{cursor: 'pointer'}}
                    onClick={() => dislike(id)}
                    >
                        <h1>Done</h1>
                    </div>
                </div>
                
            </div>
        </div>
        }
        {needsToLogin 
        ?
        <div className='w-full flex justify-center items-center backdrop-blur-sm p-3'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md'>
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
        needsToGiveNickname ?
        <GiveNicknamePrompt vehicle={data} setNeedsToGiveNickname={setNeedsToGiveNickname}/>
        :
        <div className='w-full flex justify-center items-center backdrop-blur-sm p-3'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md max-h-full flex flex-col'>
                {
                dataLoading ?
                //data is being fetched
                <div 
                className='h-full flex flex-col justify-between'>
                    <div 
                    className='md:hidden text-gray4 flex h-14 items-center cursor-pointer border-b-2 border-gray2'
                    onClick={() => navigate('/search')}
                    >
                        <div className='h-14 w-14 flex justify-center items-center'>
                            <IoIosArrowBack className='w-8 h-8'/>
                        </div>
                        <h1 className='text-[18px]'>Back to Search</h1>
                    </div>
                    <div className='h-96 flex justify-center items-center'>
                        <ClipLoader size='29px' color='#C8C8C8'/>
                    </div>
                </div>
                :
                busExists ?
                //bus with this ID exists
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
                            <h1 className='font-bold text-2xl p-4'>{data.vehicle.license_plate}</h1>
                            <div 
                            className='h-8 w-8 flex justify-center items-center mr-4 cursor-pointer'
                            onClick={favoriteClick}
                            >
                                {savedVehicles.filter((e) => e.id==data.id).length==0 ?
                                <IoMdStarOutline className='h-8 w-8 text-gray2  hover:text-gray4 transition duration-200'/>
                                :
                                <IoMdStar className='h-8 w-8 text-gray2  hover:text-gray4 transition duration-200'/>
                                }
                            </div>
                        </div>
                        <h1 className='px-4 pb-1 pt-3'><span className='font-semibold'>Vehicle Type:</span> {capitalizeFirstLetter(data.vehicle.type)}</h1>
                        <h1 className='px-4 pb-1'><span className='font-semibold'>Brand:</span> {data.vehicle.brand}</h1>
                        <h1 className='px-4 pb-1'><span className='font-semibold'>Model:</span> {data.vehicle.model}</h1>
                        <h1 className='px-4 pb-3 border-b-2 border-gray2'><span className='font-semibold'>Color:</span> {capitalizeFirstLetter(data.vehicle.color)}</h1>
                        <div className='border-b-2 border-gray2 flex justify-between items-center h-full w-full'>
                            <div className='py-3 w-full'>
                                <h1 className='px-4 pb-1'><span className='font-semibold'>Status:</span> <span className={`px-2 py-0.5 text-white rounded-md ${data.status=='active' ? 'bg-active-green' : data.status=='unavailable' ? 'bg-unavailable-red' : data.status=='waiting' ? 'bg-waiting-yellow' : data.status=='unknown' ? 'bg-gray4' : 'bg-black'}`}>{capitalizeFirstLetter(data.status)}</span></h1>
                                <h1 className='px-4'><span className='font-semibold'>Route:</span> {data.route_name}</h1>
                            </div>
                            <div 
                            className='flex justify-center h-[2.75rem] items-center my-1 mr-4 rounded-xl border-2 border-gray1 w-full max-w-[10.5rem] hover:bg-gray1 transition duration-200 cursor-pointer'
                            onClick={() => navigate(`/search/route/${data.route_id}`)}
                            >
                                <h1>View Route Page</h1>
                            </div>
                        </div>
                        <div className='flex justify-between items-center p-4'>
                            <div className='w-7 h-7'/>
                            <div className='flex'>
                                <div 
                                className={`mr-4 px-3 py-1 rounded-xl flex items-center bg-gray1 hover:bg-gray2 transition duration-200 cursor-pointer ${data.user_choice=='thumbs_up' ? 'text-black' : 'text-gray5'}`}
                                onClick={handleLikeClick}
                                >
                                    <div className='flex justify-center items-center mb-1'>
                                        <IoMdThumbsUp className='h-6 w-6'/>
                                    </div>
                                    <h1 className='pl-2'>{data.thumbs_up}</h1>
                                </div>
                                <div 
                                className={`px-3 py-1 rounded-xl flex items-center bg-gray1 hover:bg-gray2 transition duration-200 cursor-pointer ${data.user_choice=='thumbs_down' ? 'text-black' : 'text-gray5'}`}
                                onClick={handleDislikeClick}
                                >
                                    <div className='flex justify-center items-center mt-1'>
                                        <IoMdThumbsDown className='h-6 w-6'/>
                                    </div>
                                    <h1 className='pl-2'>{data.thumbs_down}</h1>
                                </div>
                            </div>
                            {isShowingComplaints ?
                            <IoIosArrowUp
                            className='w-7 h-7 text-gray2 hover:text-gray4 transition duration-200 cursor-pointer'
                            onClick={() => setShowingComplaints(!isShowingComplaints)}
                            />
                            :
                            <IoIosArrowDown
                            className='w-7 h-7 text-gray2 hover:text-gray4 transition duration-200 cursor-pointer'
                            onClick={() => setShowingComplaints(!isShowingComplaints)}
                            />
                            }
                        </div>
                        {isShowingComplaints &&
                        <div className='pb-3'>
                            {data.complaints.length==0 ?
                            <h1 className='font-semibold text-center mb-1'>There are no complaints</h1>
                            :
                            <>
                            <h1 className='font-semibold px-4 pb-1'>Common complaints by users: </h1>
                            <div className='pl-4 pr-3 flex flex-wrap w-full h-full'>
                                {data.complaints.map( e => 
                                    <div className='flex px-3 mb-1 mr-1 bg-gray1 rounded-xl'>
                                        <h1 className='pr-1 font-medium'>{e.complaint}</h1>
                                        <h1>{e.count}</h1>
                                    </div>
                                )}
                            </div>
                            </>
                            }
                        </div>
                        }
                    </div>
                    <div className='flex justify-between border-t-2 border-gray2 h-fit'>
                        <div className='ml-4 h-12 w-12'/>
                        <div 
                        className={`flex my-4 justify-center items-center rounded-xl border-2 border-gray1 w-full h-12 max-w-[10.5rem] hover:bg-gray1 transition duration-200 ${data.status=='inactive' ? 'cursor-not-allowed bg-gray1 text-gray4' : 'cursor-pointer'}`}
                        onClick = {
                            data.status == 'inactive' ?
                            () => {}
                            :
                            handleViewOnMap
                        }
                        >
                            <h1>View on map</h1>
                        </div>
                        <div className='mr-4 my-4 h-12 w-12 flex justify-center items-center'>
                            <TbCopy
                            className='h-8 w-7 lg:h-7 lg:w-7 text-gray2 hover:text-gray4 transition duration-200 cursor-pointer'
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
                        <h1 className='text-xl font-semibold'>This vehicle doesn't exist.</h1>
                    </div>
                    <div className='md:hidden h-14'/>
                </div>
                }
            </div>
        </div>
        }</>
    )
}

export default BusInfoPage