import { useContext } from "react";
import { MapContext } from "../App";
import NavigationMenuButton from "./NavigationMenuButton";
import { IoMdSearch} from 'react-icons/io'
import {IoMapOutline , IoBookmarkOutline, IoSettingsOutline} from 'react-icons/io5'
import {FaLocationArrow} from 'react-icons/fa6'

const NavigationMenu = () => {

    const {userType} = useContext(MapContext)

    return (
        <div className="h-16 md:h-14 flex justify-center md:justify-normal md:pl-2 fixed z-20 bottom-0 right-0 w-screen top-shadow bg-white">
            {
            userType=='driver' &&
            <NavigationMenuButton
            to='/go'
            Icon={FaLocationArrow}
            text='Go'
            />
            }
            <NavigationMenuButton
            to='/map'
            Icon={IoMapOutline}
            text='Map'
            />
            <NavigationMenuButton
            to='/search'
            Icon={IoMdSearch}
            text='Search'
            />
            {
            userType=='passenger' &&
            <NavigationMenuButton
            to='/saved'
            Icon={IoBookmarkOutline}
            text='Saved'
            />
            }
            <NavigationMenuButton
            to='/settings'
            Icon={IoSettingsOutline}
            text='Settings'
            />
        </div>
    )
}

export default NavigationMenu