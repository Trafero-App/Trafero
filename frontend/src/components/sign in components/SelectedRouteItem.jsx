import { MapContext } from "../../App"
import { useContext } from "react"
import { MdDelete } from "react-icons/md"

const SelectedRouteItem = ({routeData}) => {

    const value = useContext(MapContext)
    const {routes, setRoutes} = value

    return (
        
        <div className='flex h-12 hover:bg-gray1 transition duration-200 cursor-pointer'>      
            <div 
            className='flex flex-col justify-center overflow-hidden w-full pointer-events-auto pl-4 text-sm h-12'
            >
                <h1 className='font-semibold'>{routeData.route_name}</h1>
                <h1 className='text-ellipsis text-nowrap overflow-hidden'>{routeData.description}</h1>
            </div>
            <div 
            className='flex justify-center items-center h-12 w-12 min-w-12'
            >
                <div
                className='flex justify-center items-center h-8 w-8 rounded-[2rem] hover:bg-gray2 transition duration-200'
                onClick={() => setRoutes(routes.filter((e) => JSON.stringify(e)!=JSON.stringify({
                    route_id: routeData.route_id,
                    route_name: routeData.route_name,
                    description: routeData.description,
                    line: routeData.line
                })))}
                >
                    <MdDelete
                    className='h-6 w-6'
                    />
                </div>
            </div>
        </div>
    )
}

export default SelectedRouteItem