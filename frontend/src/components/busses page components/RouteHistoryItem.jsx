import { TbHistory } from "react-icons/tb"
import { IoClose } from "react-icons/io5"
import { Navigate, useNavigate } from "react-router-dom"

const RouteHistoryItem = ({item, setRoutesHistory}) => {

    const navigate = useNavigate()

    const handleRemove = (e) => {
        e.stopPropagation()// we dont wanna navigate to that page
        const oldHistory = JSON.parse(localStorage.getItem('routes-history'))
        const newHistory = oldHistory.filter((e) => JSON.stringify(e)!=JSON.stringify(item))
        //objects are compared by reference not content
        localStorage.setItem('routes-history',JSON.stringify(newHistory))
        setRoutesHistory(newHistory)
    }

    return (
        <div
        className='flex w-full h-12 hover:bg-gray1 transition duration-200 items-center cursor-pointer'
        onClick={() => navigate(`/search/route/${item.route_id}`)}
        >
            <div className='flex h-12 min-w-12 justify-center items-center'>
                <TbHistory className='h-6 w-6'/>
            </div>
            <div className='flex justify-between w-full items-center'>
                <h1 className='font-semibold truncate'>{item.route_name}</h1>
                <div className='flex h-12 w-12 justify-center items-center'>
                    <div 
                    className='flex justify-center items-center h-8 min-w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
                    onClick={handleRemove}
                    >
                        <IoClose className='h-6 w-6'/>
                    </div>
                </div>       
            </div>   
        </div>
    )
}

export default RouteHistoryItem