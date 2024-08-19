import { useContext } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { MapContext } from '../App';
import Image from '../../logo.png'

const SignInLayout = () => {

  const value = useContext(MapContext)
  const navigate = useNavigate()
  return (
    value.isLoggedIn ?
    <div className='absolute h-screen w-full z-40 bg-opacity-20 backdrop-blur-sm flex justify-center items-center bg-black'>
        <div className='w-full max-w-96 rounded-xl bg-white shadow-md'>
            <div className='w-full h-32 p-6 flex justify-center items-center'>
                <h1 className='font-medium'>You are already logged in. You can log out through Settings</h1>
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
    :
    <div className="absolute h-full w-full flex flex-col md:flex-row md:justify-around items-center justify-center p-3 backdrop-blur-sm bg-black bg-opacity-10">
        <div className='hidden w-full md:flex flex-col items-center justify-center text-white'>
            <img src={Image} className='w-56 pb-6'/>
            <h1 className='mb-6 text-5xl font-bold'>Trafero</h1>
            <h1 className='text-2xl font-semibold'>Simpler, Smarter, Safer</h1>
        </div>
        <Outlet/>
    </div>
  )
}

export default SignInLayout