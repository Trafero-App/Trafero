import { useState } from "react"
import {IoIosArrowDown, IoIosArrowUp} from 'react-icons/io'

const StatusPicker = ({
    status, handleStatusClick
}) => {

    const [isShowingStatuses, setShowingStatuses] = useState(false)

    return (
        <div className={`mr-3 rounded-xl shadow-md bg-white w-full max-w-40 pointer-events-auto ${!isShowingStatuses && 'opacity-90 hover:opacity-100'} transition duration-200`}>
            <div className={`h-10 flex justify-between items-center ${isShowingStatuses && 'border-b-2 border-gray2'}`}>
                <div className='w-10 h-10'/>
                {
                isShowingStatuses ?
                <>
                <div className='w-10 h-10 flex justify-center items-center'>
                    <IoIosArrowDown
                    className='w-6 h-6 text-gray2 hover:text-gray4 cursor-pointer transition-duration-200'
                    onClick={() => setShowingStatuses(!isShowingStatuses)}
                    />
                </div>
                
                <div className='w-10'/>
                </>
                :
                <>
                <div className='w-10 h-10 flex justify-center items-center'>
                    <IoIosArrowUp
                    className='w-6 h-6 text-gray2 hover:text-gray4 cursor-pointer transition-duration-200'
                    onClick={() => setShowingStatuses(!isShowingStatuses)}
                    />
                </div>
                <div className='w-10 h-10 flex justify-center items-center'>
                    {
                    status=='active' &&
                    <div className='w-2 h-2 bg-active-green rounded-xl'/>
                    }
                    {
                    status=='waiting' &&
                    <div className='w-2 h-2 bg-waiting-yellow rounded-xl'/>
                    }
                    {
                    status=='unavailable' &&
                    <div className='w-2 h-2 bg-unavailable-red rounded-xl'/>
                    }
                </div>
                </>
                }
            </div>
            {
            isShowingStatuses &&
            <div className='py-3'>
                <div 
                className={`h-10 flex justify-between items-center ${status=='active' ? 'bg-gray2' : 'hover:bg-gray1'} transition duration-200 cursor-pointer`}
                onClick={() => handleStatusClick('active')}
                >
                    <div className='w-10'/>
                    <h1>Active</h1>
                    <div className='h-10 w-10 flex justify-center items-center'>
                        {
                        status=='active' &&
                        <div className='w-2 h-2 bg-active-green rounded-xl'/>
                        }
                    </div>
                </div>
                <div 
                className={`h-10 flex justify-between items-center ${status=='waiting' ? 'bg-gray2' : 'hover:bg-gray1'} transition duration-200 cursor-pointer`}
                onClick={() => handleStatusClick('waiting')}
                >
                    <div className='w-10'/>
                    <h1>Waiting</h1>
                    <div className='h-10 w-10 flex justify-center items-center'>
                        {
                        status=='waiting' &&
                        <div className='w-2 h-2 bg-waiting-yellow rounded-xl'/>
                        }
                    </div>
                </div>
                <div 
                className={`h-10 flex justify-between items-center ${status=='unavailable' ? 'bg-gray2' : 'hover:bg-gray1'} transition duration-200 cursor-pointer`}
                onClick={() => handleStatusClick('unavailable')}
                >
                    <div className='w-10'/>
                    <h1>Unavailable</h1>
                    <div className='h-10 w-10 flex justify-center items-center'>
                        {
                        status=='unavailable' &&
                        <div className='w-2 h-2 bg-unavailable-red rounded-xl'/>
                        }
                    </div>
                </div>
            </div>
            }
        </div>
    )
}

export default StatusPicker