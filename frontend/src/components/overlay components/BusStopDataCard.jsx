const BusStopDataCard = ({
    chosenBusStop,
    handleViewFullRouteClick
}) => {
  const {stop_name, working_hours, active_days, expected_price} = chosenBusStop

  return (
    <div
    className='pointer-events-auto w-full max-w-96 flex rounded-xl bg-white shadow-md'
    >
      <div className='flex flex-col w-full'>
        <div className='flex justify-center items-center font-semibold h-14 lg:h-12 border-b-2 border-gray1'>
          <h1>{stop_name}</h1>
        </div>
        <h1 className='px-4 pb-1 pt-3'><span className='font-semibold'>Working hours:</span> {working_hours}</h1>
        <h1 className='px-4 pb-1'><span className='font-semibold'>Active days:</span> {active_days}</h1>
        <h1 className='px-4'><span className='font-semibold'>Expected price:</span> {expected_price}</h1>
        <div className='flex justify-center'>
            <div 
            className='flex my-4 justify-center items-center rounded-xl border-2 border-gray1 w-full h-12 max-w-[10.5rem] cursor-pointer hover:bg-gray1 transition duration-200'
            onClick={() => handleViewFullRouteClick(chosenBusStop.route_id)}
            >
                <h1>View Full Route</h1>
            </div>
        </div>
      </div>
    </div>
  )
}

export default BusStopDataCard