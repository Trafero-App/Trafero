import { useNavigate } from "react-router-dom"

const RouteResultItem = ({route}) => {
    const {route_name, description , route_id} = route
    const navigate = useNavigate()
    return (
        <div
        className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-4 text-sm h-12 cursor-pointer hover:bg-gray1 transition duration-200'
        onClick={() => navigate(`/search/route/${route_id}`)}
        >
            <div className='flex flex-col justify-center'>
                <h1 className='truncate font-semibold'>{route_name}</h1>
                <h1 className='truncate'>{description}</h1>
            </div>
        </div>
    )
}

export default RouteResultItem