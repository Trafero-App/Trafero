import { MapContext } from "../../App"
import { useState, useContext } from "react"
import { IoMdAdd } from "react-icons/io"

const SearchedRouteItem = ({routeData}) => {

    const value = useContext(MapContext)
    const {routes, setRoutes} = value
    const [added, setAdded] = useState(routes.filter((e) => JSON.stringify(e)==JSON.stringify({
        route_id: routeData.route_id,
        route_name: routeData.route_name,
        description: routeData.description,
        line: routeData.line
    })).length!=0)

    return (
        added?
        <></>
        :
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
                onClick={() => {routes.push({
                    route_id: routeData.route_id,
                    route_name: routeData.route_name,
                    description: routeData.description,
                    line: routeData.line
                });setAdded(true)}}
                >
                    <IoMdAdd
                    className='h-6 w-6'
                    />
                </div>
            </div>
        </div>
    )
}

export default SearchedRouteItem