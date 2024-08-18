import { useNavigate, useLocation, Outlet } from "react-router-dom"
import { useState, useEffect, useContext } from "react"
import {HiUserCircle} from 'react-icons/hi2'
import { RiUserFill } from "react-icons/ri"
import { IoInformationCircle } from "react-icons/io5"
import { MdVolunteerActivism } from "react-icons/md"
import { TbLogout2, TbLogin2 } from "react-icons/tb"
import { MapContext } from "../../App"

const SettingsPage = () => {

    const value = useContext(MapContext)
    const {isLoggedIn, userType, firstName, lastName} = value

    const navigate = useNavigate()
    const location = useLocation()
    const [isOnInfoPage, setOnInfoPage] = useState(true)
    useEffect(() => {
        setOnInfoPage(location.pathname!='/settings')
    },[location.pathname])


    const {setLoggedIn, setAuthenticationToken, setUserType, setSavedLocations, setSavedRoutes, setSavedVehicles, setRoutes} = value
    const signOut = () => {
        setLoggedIn(false)
        setAuthenticationToken('')
        localStorage.setItem('authentication-token','')
        setUserType('passenger')
        setSavedLocations([])
        setSavedRoutes([])
        setSavedVehicles([])
        setRoutes([])
    }

    return (
        <div className={`absolute z-20 w-full h-screen flex pointer-events-auto border-b-[64px] md:border-b-[56px] md:pr-0 backdrop-blur-sm ${!isOnInfoPage && 'justify-center md:justify-normal bg-white md:bg-transparent'}`}>
            <div className={`bg-white w-full z-10 h-full md:shadow-md max-w-96 ${isOnInfoPage ? 'hidden md:block' : ''}`}>
                <div className='flex justify-between items-center w-full h-20 border-b-2 border-gray2 mb-3'>
                    <div className='flex items-center '>
                        <div className='flex justify-center items-center h-20 w-20'>
                            <HiUserCircle className='w-16 h-16 text-gray1'/>
                        </div>
                        <div className='flex flex-col justify-center'>
                            <h1 className={isLoggedIn ? "" : 'text-gray4' }>{isLoggedIn? `${firstName} ${lastName}` : 'Not Registered'}</h1>
                            <h1 className='text-gray4 text-sm'>{userType=='driver' ? 'Driver' : 'Passenger'}</h1>
                        </div>
                    </div>
                </div>  
                {isLoggedIn &&
                <div 
                className='h-12 w-full hover:bg-gray1 flex items-center cursor-pointer transition duration-200'
                onClick={() => navigate('/settings/account')}
                >
                    <div className='h-12 w-12 flex justify-center items-center'>
                        <RiUserFill className='h-6 w-6'/>
                    </div>
                    <h1 className='font-semibold'>Account</h1>
                </div>
                }   
                <div 
                className='h-12 w-full hover:bg-gray1 flex items-center cursor-pointer transition duration-200'
                onClick={() => navigate('/settings/contribute')}
                >
                    <div className='h-12 w-12 flex justify-center items-center'>
                        <MdVolunteerActivism className='h-6 w-6'/>
                    </div>
                    <h1 className='font-semibold'>Contribute</h1>
                </div>
                <div 
                className='h-12 w-full hover:bg-gray1 flex items-center cursor-pointer transition duration-200'
                onClick={() => navigate('/settings/about-us')}
                >
                    <div className='h-12 w-12 flex justify-center items-center'>
                        <IoInformationCircle className='h-6 w-6'/>
                    </div>
                    <h1 className='font-semibold'>About Us</h1>
                </div>  
                <div className='pt-3 mt-3 border-t-2 border-gray2'>
                    {isLoggedIn ?
                    <div 
                    className='h-12 w-full hover:bg-gray1 flex items-center cursor-pointer transition duration-200'
                    onClick={signOut}
                    >
                        <div className='h-12 w-12 flex justify-center items-center'>
                            <TbLogout2 className='h-6 w-6'/>
                        </div>
                        <h1 className='font-semibold'>Sign Out</h1>
                    </div> 
                    : 
                    <div 
                    className='h-12 w-full hover:bg-gray1 flex items-center cursor-pointer transition duration-200'
                    onClick={() => navigate('/sign-in')}
                    >
                        <div className='h-12 w-12 flex justify-center items-center'>
                            <TbLogin2 className='h-6 w-6'/>
                        </div>
                        <h1 className='font-semibold'>Sign In</h1>
                    </div> 
                    }
                </div>
            </div>
            <Outlet/>
        </div>
    )
}

export default SettingsPage