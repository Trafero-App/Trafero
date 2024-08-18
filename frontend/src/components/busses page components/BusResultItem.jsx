import { useNavigate } from "react-router-dom"

const capitalizeFirstLetter = (str) => {
    if (!str) return str;
    return str.charAt(0).match(/[a-zA-Z]/) ? str.charAt(0).toUpperCase() + str.slice(1) : str;
};

const BusResultItem = ({vehicle}) => {
    const {license_plate, status, id} = vehicle
    const navigate = useNavigate()
    return (
        <div
        className='flex flex-col justify-center w-full pointer-events-auto pl-4 text-sm h-12 hover:bg-gray1 cursor-pointer'
        onClick={() => navigate(`/search/bus/${id}`)}
        >
            <h1 className='font-semibold'>{license_plate}</h1>
            <h1 className={`w-fit px-2 text-white rounded-md ${status=='active' ? 'bg-active-green' : status=='unavailable' ? 'bg-unavailable-red' : 'bg-gray4'}`}>{capitalizeFirstLetter(status)}</h1>
        </div>
    )
}

export default BusResultItem