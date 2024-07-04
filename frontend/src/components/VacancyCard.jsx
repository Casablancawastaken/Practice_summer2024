import React from 'react';
import { Box, Heading, Text, Link } from '@chakra-ui/react';

function VacancyCard({ company, vacancy, location, salary, skills, link }) {
    return (
        <Box borderWidth="1px" borderRadius="lg" p="4" mb="4" maxW={'900px'} w={'100%'}>
            <Heading as="h3" size="md" mb="2">{vacancy}</Heading>
            <Text fontSize="sm" fontWeight="bold" mb="2">{company}</Text>
            <Text fontSize="sm" mb="2">{location}</Text>
            {salary && <Text fontSize="sm" mb="2">Зарплата: {salary}</Text>}
            <Text fontSize="sm" mb="2">Скиллы: {skills}</Text>
            <Link href={link} fontSize="sm" color="blue.500" target="_blank" rel="noopener noreferrer">Подробнее</Link>
        </Box>
    );
}

export default VacancyCard;
