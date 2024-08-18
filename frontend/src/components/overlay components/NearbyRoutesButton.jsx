const NearbyRoutesButton = ({
    chosenLocation,
    handleNearbyRoutesClick
}) => {
  return (
    //crazy css tbh
    <div 
    className=' text-sm lg:text-xs mr-3 w-full max-w-[15.5rem] lg:max-w-[14.5rem] pointer-events-auto h-14 lg:h-12 rounded-xl bg-white shadow-md opacity-90 hover:opacity-100 transition duration-200 px-3'
    style={{cursor: 'pointer'}}
    onClick={handleNearbyRoutesClick}
    >
      <div className="flex flex-col justify-center h-full items-center overflow-hidden relative">
        <div className='absolute text-center'>
          <h1>Search for routes near</h1>
          <h1 className='font-semibold text-nowrap'>{chosenLocation.name}</h1>
        </div>
      </div>
    </div>
  )
}

export default NearbyRoutesButton