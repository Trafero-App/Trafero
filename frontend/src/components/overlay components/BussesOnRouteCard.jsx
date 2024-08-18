import { useNavigate } from "react-router-dom"
import { ClipLoader } from "react-spinners"
import { PiPathBold} from "react-icons/pi"
import { IoMdStarOutline, IoMdStar} from "react-icons/io"
import BusItem from './BusItem'
import { useContext } from "react"
import { MapContext } from "../../App"

const BussesOnRouteCard = ({
    isShowingBusses, busData,
    expectedTimes,
    areExpectedTimesLoading,
    chosenRoute,
    isChosenRouteLoading,
    setChosenBusIntervalId,
    setMessage, setNeedsToLogin
}) => {
    const navigate = useNavigate()
    const value = useContext(MapContext)
    const {savedRoutes, setSavedRoutes} = value

    const {isLoggedIn} = value
    const favoriteClick = () => {
        if(isLoggedIn){
            if(savedRoutes.filter((e) => e.route_id==chosenRoute.route_id).length==0){
                setSavedRoutes([{route_id: chosenRoute.route_id, route_name: chosenRoute.route_name,description: chosenRoute.description}].concat(savedRoutes))
            }
            else{
                setSavedRoutes(savedRoutes.filter((e) => e.route_id!=chosenRoute.route_id))
            }
        }
        else{
            setMessage('You must be logged in to add a route to Favorites')
            setNeedsToLogin(true)
        }
    }
  return (
    <div
    className='pointer-events-auto w-full max-w-96 flex rounded-xl bg-white shadow-md'
    >
        <div className='flex flex-col w-full'>
            <div className='flex justify-between items-center font-semibold h-14 lg:h-12 border-b-2 border-gray1'>
                {
                chosenRoute &&
                <>
                <div 
                className='h-14 w-14 lg:h-12 lg:w-12 flex justify-center items-center cursor-pointer'
                onClick={() => navigate(`/search/route/${chosenRoute.route_id}`)}
                >
                    <PiPathBold
                    className='h-7 w-7 lg:h-6 lg:w-6 text-gray4'
                    />
                </div>
                <h1>{chosenRoute.route_name}</h1>
                <div 
                className='h-14 w-14 lg:h-12 lg:w-12 flex justify-center items-center'
                onClick={favoriteClick}
                >
                    {
                    savedRoutes.filter((e) => e.route_id==chosenRoute.route_id).length==0
                    ?
                     <IoMdStarOutline
                    className='h-8 w-8 lg:h-7 lg:w-7 text-gray4'
                    style={{cursor: 'pointer'}}
                    />  
                    :
                    <IoMdStar
                    className='h-8 w-8 lg:h-7 lg:w-7 text-gray4'
                    style={{cursor: 'pointer'}}
                    />  
                    }
                    
                </div>
                </>
                }
            </div>
            <div className='my-3'>
                {isShowingBusses && busData ?
                (areExpectedTimesLoading || isChosenRouteLoading) ? 
                <div className='flex justify-center'>
                    <ClipLoader size='29px' color='#C8C8C8'/>
                </div>
                :
                !expectedTimes && chosenRoute ?
                chosenRoute.vehicles.length==0 ?
                <div className='h-12 flex justify-center items-center'>
                    <h1 className='text-gray4 text-sm'>There are no vehicles currently on this route</h1>
                </div>
                :
                <div className={`${chosenRoute.vehicles.length>3 && 'scrollable h-42 lg:h-36'}`}>
                    {chosenRoute.vehicles.map((element,index) /*index,element doesnt work lol*/  => <BusItem key={index} vehicle={element} setChosenBusIntervalId={setChosenBusIntervalId}/>)}
                </div>
                :
                expectedTimes.length==0 ?
                <div className='h-12 flex justify-center items-center'>
                    <h1 className='text-gray4 text-sm'>There are no vehicles currently on this route</h1>
                </div>
                :
                <div className={`${expectedTimes.length>3 && 'scrollable h-42 lg:h-36'}`}>
                    {expectedTimes.map((element,index) /*index,element doesnt work lol*/  => <BusItem key={index} vehicle={element} setChosenBusIntervalId={setChosenBusIntervalId}/>)}
                </div>
                :
                <div className='h-42 lg:h-36 flex justify-center items-center px-6'>
                    <h1 className='text-gray4'>You must have "Showing Busses" turned on from the bottom left corner button</h1>
                </div>
                }
            </div>
        </div>
    </div>
  )
}

export default BussesOnRouteCard 