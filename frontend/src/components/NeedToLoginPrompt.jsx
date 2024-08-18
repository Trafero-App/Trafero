import {useContext} from "react"
import {MapContext} from '../App'
import {useLocation, useNavigate} from 'react-router-dom'

const NeedToLoginPrompt = ({message, setNeedsToLogin}) => {

    const value = useContext(MapContext)

    const navigate = useNavigate()
    const location = useLocation()

    return (
        <div className='absolute h-screen w-full z-40 bg-opacity-20 backdrop-blur-sm flex justify-center items-center bg-black'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md'>
                <div className='w-full h-32 p-6 flex justify-center items-center'>
                    <h1 className='font-medium'>{message}</h1>
                </div>
                <div className='px-6 pb-6 flex items-center justify-between'>
                    <div 
                    className='mr-1.5 h-10 w-full bg-blue3 rounded-xl cursor-pointer flex justify-center items-center'
                    onClick={() => {navigate('/settings'); setNeedsToLogin(false)}}
                    >
                        <h1 className='text-white'>Go to Settings</h1>
                    </div>
                    <div 
                    className='ml-1.5 h-10 w-full border-2 border-gray1 rounded-xl hover:bg-gray1 transition duration-200 cursor-pointer flex justify-center items-center'
                    onClick={() => {
                        if(location.pathname=='/settings/account') navigate('/settings')
                        setNeedsToLogin(false)
                    }
                    }
                    >
                        <h1>Cancel</h1>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default NeedToLoginPrompt