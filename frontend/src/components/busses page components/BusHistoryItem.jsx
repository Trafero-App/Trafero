import { TbHistory } from "react-icons/tb"
import { IoClose } from "react-icons/io5"
import { useNavigate } from "react-router-dom"

const BusHistoryItem = ({item, setBussesHistory}) => {

    const navigate = useNavigate()

    const handleRemove = (e) => {
        e.stopPropagation()
        const oldHistory = JSON.parse(localStorage.getItem('busses-history'))
        const newHistory = oldHistory.filter((e) => JSON.stringify(e)!=JSON.stringify(item))
        //objects are compared by reference not content
        localStorage.setItem('busses-history',JSON.stringify(newHistory))
        setBussesHistory(newHistory)
    }

    return (
        <div
        className='flex w-full h-12 hover:bg-gray1 transition duration-200 items-center cursor-pointer'
        onClick={() => navigate(`/search/bus/${item.id}`)}
        >
            <div className='flex h-12 w-12 justify-center items-center'>
                <TbHistory className='h-6 w-6'/>
            </div>
            <div className='flex justify-between w-full items-center'>
                <h1 className='font-semibold'>{item.license_plate}</h1>
                <div className='flex h-12 w-12 justify-center items-center'>
                    <div 
                    className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
                    onClick={handleRemove}
                    >
                        <IoClose className='h-6 w-6'/>
                    </div>
                </div>       
            </div>   
        </div>
    )
}

export default BusHistoryItem