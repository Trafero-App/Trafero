import {useContext, useState} from "react"
import {MapContext} from '../App'

const GiveNicknamePrompt = ({vehicle, setNeedsToGiveNickname}) => {

    const value = useContext(MapContext)
    const {setSavedVehicles, savedVehicles} = value
    
    const [nickname, setNickname] = useState('')

    const addVehicle = () => {
        setSavedVehicles([{nickname: nickname, license_plate: vehicle.vehicle.license_plate, id: vehicle.id}].concat(savedVehicles))
    }
    return (
        <div className='absolute h-screen w-full z-40 bg-opacity-20 backdrop-blur-sm flex justify-center items-center bg-black'>
            <div className='w-full max-w-96 rounded-xl bg-white shadow-md'>
                <div className='w-full p-6'>
                    <h1 className='font-medium pb-3'>Would you like to give this vehicle a nickname?</h1>
                    <input
                    value={nickname}
                    className="w-full px-4 py-2 rounded-xl bg-gray1 focus:outline-none placeholder-gray4" 
                    onChange={(e) => setNickname(e.target.value)}
                    placeholder="Enter nickname here"
                    />
                </div>
                <div className='px-6 pb-6 flex items-center justify-between'>
                    <div 
                    className='mr-1.5 h-10 w-full bg-blue3 rounded-xl cursor-pointer flex justify-center items-center'
                    onClick={() => {addVehicle();setNeedsToGiveNickname(false)}}
                    >
                        <h1 className='text-white'>Save vehicle</h1>
                    </div>
                    <div 
                    className='ml-1.5 h-10 w-full border-2 border-gray1 hover:bg-gray1 transition duration-200 rounded-xl cursor-pointer flex justify-center items-center'
                    onClick={() => {setNeedsToGiveNickname(false)}}
                    >
                        <h1>Cancel</h1>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default GiveNicknamePrompt