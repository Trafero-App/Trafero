import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import SavedPage from './pages/SavedPage';
import NavigationMenu from './NavigationMenu';
import MapOverlay from './pages/MapOverlay';
import DriverOverlay from './pages/DriverOverlay';
import { useContext, useState } from 'react';
import { MapContext } from '../App';
import NeedToLoginPrompt from './NeedToLoginPrompt';

const Layout = () => {

  const navigate = useNavigate()
  const location = useLocation()

  const value = useContext(MapContext)
  return (
    <>
      <Outlet/>
      <SavedPage/>
      {(value.isLoggedIn && value.userType=='driver') ?
      <DriverOverlay/>
      :
      location.pathname=='/go' &&
      <div className='absolute h-screen w-full z-40 bg-opacity-20 backdrop-blur-sm flex justify-center items-center bg-black'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md'>
                <div className='w-full h-32 p-6 flex justify-center items-center'>
                    <h1 className='font-medium'>You need to be logged in as a driver to be here</h1>
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
      }
      <MapOverlay/>
      <NavigationMenu/>
    </>
  )
}

export default Layout