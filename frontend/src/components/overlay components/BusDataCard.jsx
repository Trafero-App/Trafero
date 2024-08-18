import { ClipLoader } from "react-spinners"
import { useNavigate } from "react-router-dom";
import {IoMdBus, IoMdStarOutline, IoMdStar} from "react-icons/io"
import { useContext } from "react";
import { MapContext } from "../../App";

const capitalizeFirstLetter = (str) => {
  if (!str) return str;
  return str.charAt(0).match(/[a-zA-Z]/) ? str.charAt(0).toUpperCase() + str.slice(1) : str;
};

const BusDataCard = ({
    isChosenBusDataLoading,
    chosenBusData,
    handleViewFullRouteClick,
    setMessage,
    setNeedsToLogin,
    setNeedsToGiveNickname
}) => {
  const value = useContext(MapContext)
  const {savedVehicles, setSavedVehicles} = value
  const navigate = useNavigate()

  const {isLoggedIn} = value
  const favoriteClick = () => {
    if(isLoggedIn){
      if(savedVehicles.filter((e) => e.id==chosenBusData.id).length==0){
        setNeedsToGiveNickname(true)
      }
      else{
        setSavedVehicles(savedVehicles.filter((e) => e.id!=chosenBusData.id))
      }
    }
    else{
      setMessage('You must be logged in to add a vehicle to Favorites')
      setNeedsToLogin(true)
    }
  }
  return (
    <div
    className='pointer-events-auto w-full max-w-96 flex rounded-xl bg-white shadow-md'
    >
      {!isChosenBusDataLoading ?
      <div className='flex flex-col w-full'>
        <div className='flex justify-between items-center font-semibold h-14 lg:h-12 border-b-2 border-gray1'>
          <div 
          className='h-14 w-14 lg:h-12 lg:w-12 flex justify-center items-center cursor-pointer'
          onClick={() => {navigate(`/search/bus/${chosenBusData.id}`)}}
          >
            <IoMdBus
            className='h-7 w-7 lg:h-6 lg:w-6 text-gray4'
            />
          </div>
          <h1>{`${capitalizeFirstLetter(chosenBusData.vehicle.type)} Info`}</h1>
          <div 
          className='h-14 w-14 lg:h-12 lg:w-12 flex justify-center items-center'
          onClick={favoriteClick}
          >
            {
            savedVehicles.filter((e) => e.id==chosenBusData.id).length==0
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
        </div>
        <div className='px-4 py-3 text-md md:text-sm flex'>
          <div className='w-[50%] border-r-2 border-gray1 flex flex-col'>
            <div className='flex'>
              <h1 className='font-semibold pr-1'>Brand:</h1>
              <h1 className='truncate'> {chosenBusData.vehicle.brand}</h1>
            </div>
            <div className='flex'>
              <h1 className='font-semibold pr-1'>Model:</h1>
              <h1 className='truncate'> {chosenBusData.vehicle.model}</h1>
            </div>
            <div className='flex'>
              <h1 className='font-semibold pr-1'>Color:</h1>
              <h1> {capitalizeFirstLetter(chosenBusData.vehicle.color)}</h1>
            </div>
            <div className='flex'>
              <h1 className='font-semibold pr-1'>License #:</h1>
              <h1 className='truncate'> {chosenBusData.vehicle.license_plate}</h1>
            </div>
          </div>
          <div className='flex flex-col w-[50%] pl-3'>
            <div className='flex'>
              <h1 className='font-semibold pr-1'>Status:</h1>
              <h1 className={`px-2 text-white rounded-md ${chosenBusData.status=='active' ? 'bg-active-green' : chosenBusData.status=='unavailable' ? 'bg-unavailable-red' : chosenBusData.status=='waiting' ? 'bg-waiting-yellow' : chosenBusData.status=='unknown' ? 'bg-gray4' : 'bg-black'}`}>{capitalizeFirstLetter(chosenBusData.status)}</h1>
            </div>
            <div className='flex mb-1'>
              <h1 className='font-semibold pr-1'>Route:</h1>
              <h1 className='truncate'> {chosenBusData.route_name}</h1>
            </div>
            <div 
            className='h-full flex justify-center items-center border-2 border-gray1 rounded-xl hover:bg-gray1 transition duration-200'
            style={{cursor: 'pointer'}}
            onClick={() => {handleViewFullRouteClick(chosenBusData.route_id)}}
            >
              <h1>View Full Route</h1>
            </div>
          </div>
        </div>
      </div>
      : 
      <div className='pointer-events-auto w-full max-w-96 h-48 flex justify-center items-center'>
        <ClipLoader size='29px' color='#C8C8C8'/>
      </div>
    }
    </div>
  )
}

export default BusDataCard